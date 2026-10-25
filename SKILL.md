---
name: ui-ux-web-guidelines
description: Apply Web UI/UX design guidelines focused on RWD, accessible color usage, information hierarchy, and meaningful helper text/microcopy. Use when designing, reviewing, or implementing web interfaces.
---

# UI/UX Web Guidelines Skill

Use the detailed rules in `README.md` whenever you design, review, or implement a web UI.

## Required workflow

1. Identify the screen or component's user task.
2. Classify every screen, section, card, form, and data row into:
   - primary information
   - secondary information
   - supporting information
3. Ensure the visual design makes the primary information easiest to scan and does not let secondary or supporting information compete with it.
4. Check responsive behavior for mobile, tablet, desktop, and large desktop.
5. Choose color systems by application domain as a recommendation only; final primary color must be confirmed by the user/brand owner.
6. Validate color roles and contrast:
   - normal text: at least 4.5:1
   - large text: at least 3:1
   - meaningful non-text UI elements: at least 3:1
   - never use color as the only indicator
7. Review all labels, placeholders, helper text, captions, notes, and errors for meaningful guidance.
8. Apply the repeatable scenarios in [README.md, section 11](README.md#11-可重複審查與驗收): keyboard/focus, reduced motion, async recovery, long content, and internationalization. Preserve the existing Chinese microcopy, brand decisions, and responsive rules.
9. Report scope, evidence, severity, exact file/line or screen location, and verified versus untested coverage using that section's review format. A static review or screenshot is not a runtime accessibility pass.

## Color selection rules

- Treat domain palettes as starting recommendations, not fixed rules.
- Ask or infer whether the user/brand already has a primary color, forbidden colors, competitor differentiation needs, or cultural constraints.
- Recommended examples: finance/FinTech often starts from blue, blue-green, or deep green; healthcare from blue, teal, or green; education from blue, teal, purple, or warm orange; ecommerce from the brand color with red/orange reserved for promotion; sustainability from green, teal, and earth tones.
- Always keep status colors distinct from brand colors, especially error/danger red and success green.

## Microcopy rules

- Labels state what the field is.
- Placeholders provide short examples only and must not duplicate labels.
- Helper text, captions, and notes explain constraints, format, visibility, purpose, consequence, or next step.
- Error messages explain what is wrong and how to fix it.
- For visibility-sensitive fields, explicitly say who can see the content.

## Examples

- Password helper text: `密碼需至少 12 碼，並包含英文、數字與符號。`
- Private note helper text: `此備註僅自己可見，不會顯示給客戶。`
- Public note helper text: `此備註會顯示給所有協作者，請勿填寫敏感資料。`

See `README.md` for the full checklist and source references.

## Review and capability boundaries

- Use only tools already available and authorized for the task. This skill grants no browser, network, command execution, installation, or additional write permissions.
- When interaction, assistive technology, or rendered output cannot be tested, mark the case untested and state the smallest manual verification step. Do not silently broaden permissions to complete a checklist.
- Keep design recommendations separate from confirmed defects and standards violations. Do not replace brand-owner decisions with external guideline preferences.
- This is a scoped review, not a WCAG conformance certification. Manual keyboard and assistive-technology testing remains necessary where applicable.
