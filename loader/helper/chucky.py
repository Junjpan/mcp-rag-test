from typing import List
def chucky(content: str, maxChars=500) -> List[str]:
    """ Helper function to make a larger content into a smaller chunk """
    paragraphs = content.split("\n\n") #split by by paragraphs

    chunks, text = [], ''
    for para in paragraphs:
        if len(text) + len(para) + 2 <= maxChars:
            text += para + "\n\n"
        else:
            if text:
                chunks.append(text.strip())
            text = para + "\n\n"
   # Add any remaining text as a chunk
    if text:
        chunks.append(text.strip())

    return chunks
