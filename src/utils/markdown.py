import re

def escape_markdown_v2(text):
    """
    텔레그램 MarkdownV2 형식에서 특수 문자를 이스케이프합니다.
    """
    if not text:
        return ""
        
    # MarkdownV2에서 이스케이프가 필요한 특수 문자
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    # 각 특수 문자 앞에 백슬래시 추가
    for char in special_chars:
        text = text.replace(char, '\\' + char)
        
    return text

def truncate_text(text, max_length=4000):
    """
    텔레그램 메시지 길이 제한을 준수하도록 텍스트를 자릅니다.
    """
    if not text:
        return ""
        
    if len(text) <= max_length:
        return text
        
    return text[:max_length-3] + "..."
