"""把笔记中的纯文本公式改写成适合 Word 阅读的形式。

策略（不依赖 LaTeX 排版）：
1. 清掉残留 $...$ / \\frac 等
2. 希腊字母与常用算符换成 Unicode
3. 在 Word 中用原生下标/上标（font.subscript / superscript）
4. 简单分子/分母尽量做成 OMML 分式，便于人眼阅读
"""

from __future__ import annotations

import re
from typing import Any

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

# ---------- 文本层：先把 Markdown/伪 LaTeX 变成人话 ----------

GREEK = {
    r"\alpha": "α",
    r"\beta": "β",
    r"\gamma": "γ",
    r"\delta": "δ",
    r"\epsilon": "ε",
    r"\varepsilon": "ε",
    r"\zeta": "ζ",
    r"\eta": "η",
    r"\theta": "θ",
    r"\iota": "ι",
    r"\kappa": "κ",
    r"\lambda": "λ",
    r"\mu": "μ",
    r"\nu": "ν",
    r"\xi": "ξ",
    r"\pi": "π",
    r"\rho": "ρ",
    r"\sigma": "σ",
    r"\tau": "τ",
    r"\phi": "φ",
    r"\varphi": "φ",
    r"\chi": "χ",
    r"\psi": "ψ",
    r"\omega": "ω",
    r"\Alpha": "Α",
    r"\Beta": "Β",
    r"\Gamma": "Γ",
    r"\Delta": "Δ",
    r"\Theta": "Θ",
    r"\Lambda": "Λ",
    r"\Xi": "Ξ",
    r"\Pi": "Π",
    r"\Sigma": "Σ",
    r"\Phi": "Φ",
    r"\Psi": "Ψ",
    r"\Omega": "Ω",
}

OPS = [
    (r"\\times", "×"),
    (r"\\cdot", "·"),
    (r"\\pm", "±"),
    (r"\\mp", "∓"),
    (r"\\leq", "≤"),
    (r"\\geq", "≥"),
    (r"\\neq", "≠"),
    (r"\\approx", "≈"),
    (r"\\propto", "∝"),
    (r"\\infty", "∞"),
    (r"\\sqrt", "√"),
    (r"\\partial", "∂"),
    (r"\\sum", "∑"),
    (r"\\prod", "∏"),
    (r"\\int", "∫"),
    (r"\\rightarrow", "→"),
    (r"\\leftarrow", "←"),
    (r"\\leftrightarrow", "↔"),
    (r"\\Rightarrow", "⇒"),
    (r"\\ldots", "…"),
    (r"\\dots", "…"),
    (r"\\,", " "),
    (r"\\;", " "),
    (r"\\!", ""),
    (r"\\left", ""),
    (r"\\right", ""),
    (r"\\mathrm", ""),
    (r"\\mathbf", ""),
    (r"\\boldsymbol", ""),
    (r"\\text", ""),
    (r"\\operatorname", ""),
]

# ASCII 运算符美化（仅在公式上下文中使用）
ASCII_OPS = [
    (re.compile(r"(?<![A-Za-z])\*(?![A-Za-z])"), "×"),
    (re.compile(r"\bpropto\b"), "∝"),
    (re.compile(r"(?<![A-Za-z])<=(?![A-Za-z])"), "≤"),
    (re.compile(r"(?<![A-Za-z])>=(?![A-Za-z])"), "≥"),
    (re.compile(r"(?<![A-Za-z])!=(?![A-Za-z])"), "≠"),
]


def latexish_to_readable(text: str) -> str:
    """Strip LaTeX wrappers and replace common commands with Unicode."""
    if not text:
        return text

    # $...$ / $$...$$ / \(...\) / \[...\]
    text = re.sub(r"\$\$([\s\S]*?)\$\$", r"\1", text)
    text = re.sub(r"\$([^$]+)\$", r"\1", text)
    text = re.sub(r"\\\((.+?)\\\)", r"\1", text)
    text = re.sub(r"\\\[(.+?)\\\]", r"\1", text)

    # Greek / ops first (so \\epsilon_L becomes ε_L)
    for src, dst in sorted(GREEK.items(), key=lambda x: -len(x[0])):
        text = text.replace(src, dst)
    for src, dst in OPS:
        text = text.replace(src, dst)

    # \frac{a}{b} → (a)/(b)  （后续 OMML 再尝试做成真正分式）
    for _ in range(8):
        new = re.sub(r"\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}", r"(\1)/(\2)", text)
        if new == text:
            break
        text = new

    # \sqrt{x} → √(x)
    text = re.sub(r"\\sqrt\s*\{([^{}]+)\}", r"√(\1)", text)

    # _{abs} / ^{ -3 } → _abs / ^-3  (keep underscore form for Word scripts)
    text = re.sub(r"_\{([^{}]+)\}", r"_\1", text)
    text = re.sub(r"\^\{([^{}]+)\}", r"^\1", text)

    # Remaining \command{x} → x ; bare \command → removed if unknown
    text = re.sub(r"\\[a-zA-Z]+\s*\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\[a-zA-Z]+", "", text)

    # Drop any leftover braces
    text = text.replace("{", "").replace("}", "")
    # Common spelled-out greek in formulas
    text = re.sub(r"(?<![A-Za-z])alpha(?![A-Za-z])", "α", text)
    text = re.sub(r"(?<![A-Za-z])beta(?![A-Za-z])", "β", text)
    text = re.sub(r"(?<![A-Za-z])gamma(?![A-Za-z])", "γ", text)
    text = re.sub(r"(?<![A-Za-z])delta(?![A-Za-z])", "δ", text)
    text = re.sub(r"(?<![A-Za-z])epsilon(?![A-Za-z])", "ε", text)
    text = re.sub(r"(?<![A-Za-z])sigma(?![A-Za-z])", "σ", text)
    text = re.sub(r"(?<![A-Za-z])omega(?![A-Za-z])", "ω", text)
    text = re.sub(r"(?<![A-Za-z])lambda(?![A-Za-z])", "λ", text)
    text = re.sub(r"(?<![A-Za-z])mu(?![A-Za-z])", "μ", text)
    text = re.sub(r"(?<![A-Za-z])tau(?![A-Za-z])", "τ", text)
    text = re.sub(r"(?<![A-Za-z])pi(?![A-Za-z])", "π", text)

    text = re.sub(r"[ \t]+", " ", text)
    return text


def looks_like_formula(text: str) -> bool:
    """Heuristic: equation-ish content worth math formatting."""
    t = text.strip()
    if not t or len(t) > 280:
        return False
    if re.search(r"[\u4e00-\u9fff]{8,}", t):
        # long Chinese prose — not a formula line
        if "=" not in t and "_" not in t and "^" not in t:
            return False
    score = 0
    if "=" in t or "≈" in t or "∝" in t or "≤" in t or "≥" in t:
        score += 2
    if "_" in t or "^" in t:
        score += 2
    if re.search(r"[α-ωΑ-ΩεμσΔΣΠ∂∑∏∫√×·±]", t):
        score += 1
    if re.search(
        r"\b(g_abs|g_lum|g_ph|g_corr|EQE|NEP|LDR|PLQE|I_ph|I_dark|Abs_|R_on)\b",
        t,
    ):
        score += 2
    if re.search(r"\d+\^\d+|\d+\^\{?-?\d+", t):
        score += 1
    return score >= 2


# ---------- Word 层：上下标 + 可选 OMML 分式 ----------

MATH_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

# token patterns for base_sub / base^sup / 10^{-3}
TOKEN_RE = re.compile(
    r"("
    r"[A-Za-zΑ-Ωα-ωεμσΔ∂∑∏πΠ][A-Za-z0-9Α-Ωα-ωεμσ]*"  # identifier
    r"(?:_(?:\{[^}]+\}|[A-Za-z0-9]+(?:/[A-Za-z0-9]+)?(?:,[A-Za-z0-9]+)?))?"  # optional _sub
    r"(?:\^(?:\{[^}]+\}|[A-Za-z0-9+-]+))?"  # optional ^sup
    r"|"
    r"\((?:[^()]|\([^()]*\))*\)"  # simple paren group
    r"(?:_(?:\{[^}]+\}|[A-Za-z0-9]+))?"
    r"(?:\^(?:\{[^}]+\}|[A-Za-z0-9+-]+))?"
    r"|"
    r"\d+(?:\.\d+)?"  # number
    r"(?:\^(?:\{[^}]+\}|[A-Za-z0-9+-]+))?"
    r")"
)


def _strip_braces(s: str) -> str:
    s = s.strip()
    if s.startswith("{") and s.endswith("}"):
        return s[1:-1]
    return s


def _parse_scripted(token: str) -> tuple[str, str | None, str | None]:
    """Split token into base, subscript, superscript."""
    base, sub, sup = token, None, None
    # Handle base_sub^sup or base^sup or base_sub
    m = re.match(
        r"^(?P<base>.+?)"
        r"(?:_(?P<sub>\{[^}]+\}|[A-Za-z0-9]+(?:/[A-Za-z0-9]+)?(?:,[A-Za-z0-9]+)?))?"
        r"(?:\^(?P<sup>\{[^}]+\}|[A-Za-z0-9+-]+))?$",
        token,
    )
    if not m:
        return token, None, None
    base = m.group("base")
    if m.group("sub"):
        sub = _strip_braces(m.group("sub"))
    if m.group("sup"):
        sup = _strip_braces(m.group("sup"))
    # If base itself ends with )^ already consumed; ok
    return base, sub, sup


def _set_math_run_font(run, *, size_pt: float = 11, italic: bool = False) -> None:
    run.font.size = Pt(size_pt)
    run.font.name = "Cambria Math"
    run.italic = italic
    r = run._element
    rpr = r.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    rfonts.set(qn("w:ascii"), "Cambria Math")
    rfonts.set(qn("w:hAnsi"), "Cambria Math")
    rfonts.set(qn("w:eastAsia"), "Cambria Math")
    # fallback
    rfonts.set(qn("w:cs"), "Cambria Math")


def _add_plain_run(paragraph, text: str, *, size_pt: float = 11, italic: bool = False) -> None:
    if not text:
        return
    run = paragraph.add_run(text)
    _set_math_run_font(run, size_pt=size_pt, italic=italic)


def _add_scripted_run(
    paragraph,
    base: str,
    sub: str | None,
    sup: str | None,
    *,
    size_pt: float = 11,
) -> None:
    italic_base = bool(re.fullmatch(r"[A-Za-zΑ-Ωα-ωεμσΔ∂πΠ]+", base)) and len(base) <= 3
    _add_plain_run(paragraph, base, size_pt=size_pt, italic=italic_base)
    if sub is not None:
        run = paragraph.add_run(sub)
        _set_math_run_font(run, size_pt=size_pt * 0.9)
        run.font.subscript = True
    if sup is not None:
        run = paragraph.add_run(sup)
        _set_math_run_font(run, size_pt=size_pt * 0.9)
        run.font.superscript = True


def _omml_run(text: str, *, italic: bool = False) -> Any:
    r = OxmlElement("m:r")
    rpr = OxmlElement("m:rPr")
    if not italic:
        sty = OxmlElement("m:sty")
        sty.set(qn("m:val"), "p")
        rpr.append(sty)
    r.append(rpr)
    wrpr = OxmlElement("w:rPr")
    fonts = OxmlElement("w:rFonts")
    fonts.set(qn("w:ascii"), "Cambria Math")
    fonts.set(qn("w:hAnsi"), "Cambria Math")
    wrpr.append(fonts)
    r.append(wrpr)
    t = OxmlElement("m:t")
    t.set(qn("xml:space"), "preserve")
    t.text = text
    r.append(t)
    return r


def _omml_fraction(num: str, den: str) -> Any:
    """Build a simple OMML fraction element (m:f)."""
    f = OxmlElement("m:f")
    fpr = OxmlElement("m:fPr")
    f.append(fpr)
    num_e = OxmlElement("m:num")
    den_e = OxmlElement("m:den")
    # put scripted tokens as plain for simplicity inside fraction
    num_e.append(_omml_run(num, italic=True))
    den_e.append(_omml_run(den, italic=True))
    f.append(num_e)
    f.append(den_e)
    return f


def _try_append_omml_fraction(paragraph, num: str, den: str) -> None:
    omath = OxmlElement("m:oMath")
    # Apply humanized subscripts inside num/den as plain Unicode-ish text
    num_h = _scripts_to_unicode_fallback(num)
    den_h = _scripts_to_unicode_fallback(den)
    omath.append(_omml_fraction(num_h, den_h))
    paragraph._p.append(omath)


_SUB_MAP = str.maketrans(
    "0123456789+-=()aehijklmnoprstuvx",
    "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ",
)
_SUP_MAP = str.maketrans(
    "0123456789+-=()ni",
    "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ",
)


def _scripts_to_unicode_fallback(text: str) -> str:
    """For OMML inner text / fallback: A_L → Aₗ when possible."""
    def repl(m: re.Match[str]) -> str:
        base, sub = m.group(1), m.group(2)
        mapped = sub.translate(_SUB_MAP)
        if mapped != sub and all(c in "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ" or not c.isascii() for c in mapped):
            return base + mapped
        return f"{base}({sub})"

    text = re.sub(
        r"([A-Za-zΑ-Ωα-ωεμσΔ∂πΠ][A-Za-z0-9]*)_([A-Za-z0-9]+(?:/[A-Za-z0-9]+)?)",
        repl,
        text,
    )
    return text


def add_formula_runs(paragraph, text: str, *, size_pt: float = 11) -> None:
    """
    Write a formula string into a paragraph with human-friendly Word formatting.
    """
    text = latexish_to_readable(text)
    for rx, repl in ASCII_OPS:
        text = rx.sub(repl, text)

    # Prefer stacked fraction for "... = (num)/[den]" or "(num)/(den)"
    if looks_like_formula(text) and "/" in text:
        frac = re.match(
            r"^\s*(?P<head>.*?[=≈∝]\s*)?"
            r"(?:\((?P<n1>[^()]+)\)|(?P<n2>[A-Za-z0-9Α-Ωα-ωεμσΔ∂πΠ_^+×·\-−]+))"
            r"\s*/\s*"
            r"(?:\[(?P<d1>[^\]]+)\]|\((?P<d2>[^()]+)\)|(?P<d3>[A-Za-z0-9Α-Ωα-ωεμσΔ∂πΠ_^+×·\-−.]+))"
            r"\s*$",
            text,
        )
        if frac:
            head = frac.group("head") or ""
            num = frac.group("n1") or frac.group("n2") or ""
            den = frac.group("d1") or frac.group("d2") or frac.group("d3") or ""
            if num and den and len(num) <= 80 and len(den) <= 80:
                if head:
                    _emit_scripted_sequence(paragraph, head, size_pt=size_pt)
                _try_append_omml_fraction(paragraph, num, den)
                return

    _emit_scripted_sequence(paragraph, text, size_pt=size_pt)


def _emit_scripted_sequence(paragraph, text: str, *, size_pt: float = 11) -> None:
    pos = 0
    for m in TOKEN_RE.finditer(text):
        if m.start() > pos:
            _add_plain_run(paragraph, text[pos : m.start()], size_pt=size_pt)
        token = m.group(0)
        base, sub, sup = _parse_scripted(token)
        # Parenthesized group with scripts: render base as text then scripts
        if base.startswith("(") and (sub or sup):
            _add_plain_run(paragraph, base, size_pt=size_pt)
            if sub:
                run = paragraph.add_run(sub)
                _set_math_run_font(run, size_pt=size_pt * 0.9)
                run.font.subscript = True
            if sup:
                run = paragraph.add_run(sup)
                _set_math_run_font(run, size_pt=size_pt * 0.9)
                run.font.superscript = True
        elif sub or sup:
            _add_scripted_run(paragraph, base, sub, sup, size_pt=size_pt)
        else:
            # bare identifier / number
            italic = bool(re.fullmatch(r"[A-Za-zΑ-Ωα-ωεμσΔ∂πΠ]+", token)) and len(token) <= 3
            _add_plain_run(paragraph, token, size_pt=size_pt, italic=italic)
        pos = m.end()
    if pos < len(text):
        _add_plain_run(paragraph, text[pos:], size_pt=size_pt)


def humanize_inline_text(text: str) -> str:
    """Light cleanup for prose that may contain formula scraps (no Word runs)."""
    return latexish_to_readable(text)
