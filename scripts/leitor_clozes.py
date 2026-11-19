
import re
import os

def clean_cloze(text):
    """
    Removes == markers from cloze deletions, keeping the text inside.
    Example: "Deus é ==fiel==" -> "Deus é fiel"
    """
    return text.replace("==", "")

def extract_verses(filepath):
    """
    Extracts verses from a markdown file with the specific Life of Faith format.
    Returns a list of dictionaries with 'reference' and 'text'.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by blocks (usually separated by newlines or specific markers)
    # The format seems to be >[!Bible] Reference\n>Text...\n>*card X*
    
    # Regex to find blocks.
    # We want to capture everything starting with >[!Bible] until:
    # 1. Another >[!Bible]
    # 2. A >*card marker
    # 3. An <!--SR marker
    # 4. A double newline (paragraph break)
    # 5. End of string
    
    # Logic: 
    # Match >[!Bible] (Group 1: Reference) \n (Group 2: Content)
    # Lookahead for one of the terminators.
    
    pattern = re.compile(r'>\[!Bible\](.*?)\n(.*?)(?=\n(?:>\[!Bible\]|>\*card|<!--SR|\n|$))', re.DOTALL)
    
    matches = pattern.findall(content)
    verses = []
    
    for reference_raw, text_raw in matches:
        # Clean reference
        # Remove links: [Ref](url) -> Ref
        reference = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', reference_raw).strip()
        reference = reference.replace("==", "").replace("NVI", "").strip() # Clean clozes in reference if any
        
        # Clean text
        # Remove '>' at start of lines
        text_lines = [line.strip().replace('>', '', 1).strip() for line in text_raw.split('\n')]
        text = ' '.join(text_lines)
        
        # Clean clozes
        text = clean_cloze(text)
        
        # Remove double spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        if text:
            verses.append({
                'reference': reference,
                'text': text
            })
            
    return verses

if __name__ == "__main__":
    file_path = "/Users/halom/Documents/xp/vidaLog/30 Áreas/Vida de fé/📖 Livro 4 - o guerreiro puro.md"
    if not os.path.exists(file_path):
        file_path = "/Users/halom/Documents/xp/vidaLog/30 Áreas/Vida de fé/📖 Livro 4 - o guerreiro puro.md"
    if not os.path.exists(file_path):
        file_path = "/Users/halom/Documents/xp/vidaLog/🗡️ Vida de fé/📖 Livro 4 - o guerreiro puro.md"
    
    if os.path.exists(file_path):
        verses = extract_verses(file_path)
        print(f"Found {len(verses)} verses.")
        for i, v in enumerate(verses[:3]):
            print(f"--- Verse {i+1} ---")
            print(f"Ref: {v['reference']}")
            print(f"Text: {v['text']}")
    else:
        print("File not found for testing.")
