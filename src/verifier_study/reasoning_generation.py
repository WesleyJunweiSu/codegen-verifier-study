"""Bounded Qwen reasoning generation without retaining vocabulary logits on the GPU."""
import hashlib
import time
from verifier_study.generation import LocalCausalLM, prompt_hash, extract_code, parses_as_python


def final_answer(output_ids, tokenizer, think_end_id):
    """Unfinished reasoning is an empty, failed answer, never executable Python."""
    if think_end_id not in output_ids:
        return '', False
    end = len(output_ids) - output_ids[::-1].index(think_end_id)
    return tokenizer.decode(output_ids[end:], skip_special_tokens=True).strip(), True


class ReasoningLM(LocalCausalLM):
    def generate_reasoning(self, *, task_id, messages, sample_index, seed, generation_kind, max_new_tokens=2048):
        torch = self.torch
        rendered = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=True)
        inputs = self.tokenizer(rendered, return_tensors='pt').to('cuda')
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.cuda.reset_peak_memory_stats()
        started = time.perf_counter()
        with torch.inference_mode():
            output = self.model.generate(**inputs, do_sample=True, temperature=0.6, top_p=0.95, top_k=20,
                 max_new_tokens=max_new_tokens, return_dict_in_generate=False, output_scores=False, output_logits=False,
                 pad_token_id=self.tokenizer.eos_token_id)
        torch.cuda.synchronize()
        elapsed = time.perf_counter() - started
        ids = output[0, inputs.input_ids.shape[1]:].tolist()
        end_id = self.tokenizer.convert_tokens_to_ids('</think>')
        answer, completed = final_answer(ids, self.tokenizer, end_id)
        code = extract_code(answer)
        return {'task_id': task_id, 'sample_index': sample_index, 'seed': seed,
                'generation_kind': generation_kind, 'model_id': self.model_id,
                'prompt_sha256': prompt_hash(messages), 'rendered_prompt_sha256': hashlib.sha256(rendered.encode()).hexdigest(),
                'raw_output': self.tokenizer.decode(ids, skip_special_tokens=False), 'code': code,
                'code_parses': bool(code) and parses_as_python(code), 'thinking_complete': completed,
                'input_tokens': int(inputs.input_ids.shape[1]), 'output_tokens': len(ids),
                'mean_token_entropy': None, 'wall_seconds': elapsed, 'peak_vram_bytes': int(torch.cuda.max_memory_allocated())}
