import torch
from torch import nn
from .txt import ContextTransformer, SequenceTransformerHistory
from .mmoe import MMoE


class TxTBottom(nn.Module):
    def __init__(self, ctx_nums, seq_num, cross_size=200, is_candidate_mode=True,
                 context_transformer_kwargs=None, sequence_transformer_kwargs=None):
        super().__init__()
        context_transformer_kwargs = context_transformer_kwargs if context_transformer_kwargs else {}
        sequence_transformer_kwargs = sequence_transformer_kwargs if sequence_transformer_kwargs else {}
        self.is_candidate_mode = is_candidate_mode
        self.features_dim = cross_size
        self.context_transformer = ContextTransformer(
            ctx_nums=ctx_nums,
            cross_size=cross_size,
            **context_transformer_kwargs,
        )
        self.sequence_transformer = SequenceTransformerHistory(
            seq_num=seq_num,
            cross_size=cross_size,
            **sequence_transformer_kwargs,
        )
        if is_candidate_mode:
            # self.candidate_dense = nn.Linear(
            #     in_features=self.sequence_transformer.seq_embed_size,
            #     out_features=cross_size
            # )
            pass

    def forward(self, ctx_in, seq_in, vl_in, candidate_in, seq_history=None):
        """
        :param ctx_in: list, a list of Tensor of shape [batch_size, 1]
        :param seq_in: Tensor, shape [batch_size, seq_len]
        :param vl_in: Tensor, shape [batch_size]
        :param candidate_in: Tensor, shape [batch_size]
        :param seq_history: Tensor, shape [batch_size, history_len]
        :return:
        """
        # input [[B, 1] * C] and [B, 5]
        ctx_out = self.context_transformer(ctx_in=ctx_in)
        seq_out = self.sequence_transformer(seq_in=seq_in, vl_in=vl_in, seq_history=seq_history)
        outs = torch.mul(seq_out, ctx_out)  # -> [B, cross_size]
        if self.is_candidate_mode:
            candidate_embed = self.sequence_transformer.seq_embedding(candidate_in)
            outs = torch.concat([outs, candidate_embed], dim=1)  # -> [B, seq_embed_size]
        return outs


class MultiTaskTxT(nn.Module):
    def __init__(self, ctx_nums, seq_num, expert_num, expert_hidden_sizes,
                 task_num, task_hidden_sizes, task_last_activations,
                 cross_size=200, is_candidate_mode=True,
                 context_transformer_kwargs=None, sequence_transformer_kwargs=None):
        super().__init__()
        self.is_candidate_mode = is_candidate_mode
        self.shared_bottom = TxTBottom(
            ctx_nums=ctx_nums,
            seq_num=seq_num,
            cross_size=cross_size,
            is_candidate_mode=is_candidate_mode,
            context_transformer_kwargs=context_transformer_kwargs,
            sequence_transformer_kwargs=sequence_transformer_kwargs,
        )
        mmoe_input_size = cross_size + self.shared_bottom.sequence_transformer.seq_embed_size
        self.mmoe = MMoE(
            input_size=mmoe_input_size,
            expert_num=expert_num,
            expert_hidden_sizes=expert_hidden_sizes,
            task_num=task_num,
            task_hidden_sizes=task_hidden_sizes,
            task_last_activations=task_last_activations,
        )

    def forward(self, ctx_in, seq_in, vl_in, candidate_in, seq_history=None):
        bottom_features = self.shared_bottom(ctx_in, seq_in, vl_in, candidate_in, seq_history)
        outs = self.mmoe(bottom_features)
        return outs
