def render(template: str, **kwargs) -> str:
    """把 {key} 占位符替换成实际内容"""
    text = template
    for key, value in kwargs.items():
        text = text.replace("{" + key + "}", str(value))
    return text