import tiktoken
from tiktoken.load import load_tiktoken_bpe
import functools

class TokenGuard:

    def __init__(
        self,
        tokenizer_path,
        model_limit=8000,
        response_reserve=1000
    ):
        self.model_limit = model_limit
        self.response_reserve = response_reserve
        self.max_context = model_limit - response_reserve
        

        # cargar tokenizer llama3
        mergeable_ranks = load_tiktoken_bpe(tokenizer_path)

        self.encoder = tiktoken.Encoding(
            name="llama3",
            pat_str=r"(?i:'s|'t|'re|'ve|'m|'ll|'d)|[^\r\n\p{L}\p{N}]?\p{L}+|\p{N}{1,3}| ?[^\s\p{L}\p{N}]+[\r\n]*|\s*[\r\n]+|\s+(?!\S)|\s+",
            mergeable_ranks=mergeable_ranks,
            special_tokens={}
        )

    @functools.lru_cache(maxsize=1000)
    def estimate_tokens(self, text):
        if not text:
            return 0

        return len(self.encoder.encode(text))


    def summary_too_large(self, summary):

        tokens = self.estimate_tokens(summary)

        return tokens > 1500


    def estimate_context_tokens(
        self,
        history,
        summary,
        system_prompt
    ):

        total = self.estimate_tokens(system_prompt)

        total += self.estimate_tokens(summary)

        for m in history:
            # Sumamos los tokens del contenido + ~4 tokens (overhead de metadatos/etiquetas/roles del LLM)
            total += self.estimate_tokens(m["content"]) + 4

        return total


    def should_summarize(self, history, summary, system_prompt):

        tokens = self.estimate_context_tokens(
            history,
            summary,
            system_prompt
        )

        return tokens > self.max_context


    def should_trim(
        self,
        history,
        summary,
        system_prompt
    ):

        tokens = self.estimate_context_tokens(
            history,
            summary,
            system_prompt
        )

        return tokens > self.model_limit