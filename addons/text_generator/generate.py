import argparse
import json
import os
from src.load_model import get_model
from src.config import DEFAULT_PARAMS

def get_paraphrase_prompt(input_text, variants, target_language, level, style, genre, form, length):
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "paraphrase.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        template = f.read()
    return template.format(
        source_language="русском", # Assuming Russian input based on example
        input_text=input_text,
        variants=variants,
        target_language=target_language,
        level=level,
        style=style,
        genre=genre,
        form=form,
        length=length
    )

def generate_text(args):
    model = get_model()
    
    # Build prompt
    if args.input_text:
        user_prompt = get_paraphrase_prompt(args.input_text, args.variants, args.target_language, args.level, args.style, args.genre, args.form, args.length)
    elif args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            input_text = f.read()
        user_prompt = get_paraphrase_prompt(input_text, args.variants, args.target_language, args.level, args.style, args.genre, args.form, args.length)
    else:
        user_prompt = f"Topic: {args.topic}\nLevel: {args.level}\nStyle: {args.style}\nGenerate {args.variants} natural text variants for this situation.\n\n"
        
    system_prompt = "You are a helpful text generator. Output the requested text directly, without any thinking process."
    
    response = model.create_chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=DEFAULT_PARAMS["temperature"],
        max_tokens=DEFAULT_PARAMS["max_tokens"],
        top_p=DEFAULT_PARAMS["top_p"]
    )

    text = response['choices'][0]['message']['content']
    
    # Post-processing to remove <think> blocks
    if "</think>" in text:
        text = text.split("</think>")[-1]
    elif "<think>" in text:
        text = text.split("<think>")[-1]
    
    return [text]

def main():
    parser = argparse.ArgumentParser(description="Companion Text Generator CLI")
    parser.add_argument("--topic", help="Topic for text generation")
    parser.add_argument("--input", help="Input file path")
    parser.add_argument("--input-text", help="Input text for paraphrasing")
    parser.add_argument("--level", default="A2", help="Language level")
    parser.add_argument("--variants", type=int, default=1, help="Number of variants")
    parser.add_argument("--style", default="conversation", help="Style")
    parser.add_argument("--genre", default="general", help="Genre")
    parser.add_argument("--form", default="dialogue", help="Form")
    parser.add_argument("--length", default="short", help="Length")
    parser.add_argument("--target-language", default="nl", help="Target language")
    parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    if not args.topic and not args.input and not args.input_text:
        parser.error("You must provide either --topic, --input, or --input-text")
        
    print(f"Generating variants...")
    variants = generate_text(args)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            for i, v in enumerate(variants):
                f.write(f"--- Variant {i+1} ---\n{v}\n\n")
        print(f"Variants saved to {args.output}")
    else:
        for i, v in enumerate(variants):
            print(f"\n--- Variant {i+1} ---\n{v}")

if __name__ == "__main__":
    main()
