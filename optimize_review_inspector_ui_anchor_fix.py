from pathlib import Path

root = Path.cwd()
tsx = root / "features/workspace/workspace-shell.tsx"
css = root / "features/workspace/workspace-shell.css"

if not tsx.exists():
    raise SystemExit("[失败] 找不到 features/workspace/workspace-shell.tsx")

s = tsx.read_text(encoding="utf-8")

# 1) 第四步右侧：使用稳定锚点替换
start = s.find('<div className="result-size-editor">')
if start == -1:
    raise SystemExit("[失败] 找不到 result-size-editor")

danger = s.find('<button className="danger-btn"', start)
if danger == -1:
    raise SystemExit("[失败] 找不到结果卡删除按钮")

end = s.find('</div>', danger)
if end == -1:
    raise SystemExit("[失败] 找不到结果卡操作区结束位置")
end += len('</div>')

replacement = '''<section className="inspector-section">
              <div className="inspector-section-title">画板</div>
              <div className="result-size-editor inspector-grid">
                <label>W<input type="number" min="1" value={m.width||0} onChange={e=>updateMaterial(m.id,{width:Number(e.target.value)})}/></label>
                <span>×</span>
                <label>H<input type="number" min="1" value={m.height||0} onChange={e=>updateMaterial(m.id,{height:Number(e.target.value)})}/></label>
                <select value={m.unit||"mm"} onChange={e=>updateMaterial(m.id,{unit:e.target.value as "mm"|"px"})}>
                  <option value="mm">mm</option>
                  <option value="px">px</option>
                </select>
              </div>
            </section>

            <section className="inspector-section">
              <div className="inspector-section-title">颜色</div>
              <div className="result-palette-editor">
                <label>底色<PaletteSelect value={m.backgroundPreference} onChange={v=>updateMaterial(m.id,{backgroundPreference:v})}/></label>
                <label>图形<PaletteSelect value={m.graphicPreference} onChange={v=>updateMaterial(m.id,{graphicPreference:v})}/></label>
              </div>
            </section>

            <section className="inspector-section">
              <div className="inspector-section-title">内容</div>
              <div className="text-mode-switch inspector-text-switch">
                <button className={m.withText!==false?"selected":""} onClick={()=>updateMaterial(m.id,{withText:true})}>文字</button>
                <button className={m.withText===false?"selected":""} onClick={()=>updateMaterial(m.id,{withText:false})}>纯图形</button>
              </div>
            </section>

            <section className="inspector-section inspector-actions-section">
              <div className="inspector-section-title">快速操作</div>
              <div className="inspector-actions">
                <button className="primary-adjust" onClick={()=>{setEditing(m);setAdjustText("")}} disabled={isBusy}>调整设计</button>
                <button className={approved.includes(m.id)?"approved":""} onClick={()=>keep(m.id)} disabled={isBusy}>
                  {approved.includes(m.id)?"已保留 ✓":"保留"}
                </button>
                <button onClick={()=>{const x=layouts[m.id];setCopyEditing(m);setCopyDraft({headline:x?.headline||"",subline:x?.subline||"",microcopy:x?.microcopy||""})}} disabled={isBusy}>文字</button>
                <button onClick={()=>redo(m)} disabled={isBusy}>{isBusy?"生成中…":"重做"}</button>
                <button className="danger-btn" onClick={()=>remove(m.id)} disabled={isBusy}>删除</button>
              </div>
            </section>'''

s = s[:start] + replacement + s[end:]

# 2) 调整弹窗：把方案概念/设计说明放进去
modal_start = s.find('<span className="rule-tag">局部调整 · {editing.name}</span>')
if modal_start == -1:
    modal_start = s.find('<span className="rule-tag">调整设计 · {editing.name}</span>')
if modal_start == -1:
    raise SystemExit("[失败] 找不到调整弹窗标题")

quick = s.find('<div className="quick-adjust">', modal_start)
if quick == -1:
    raise SystemExit("[失败] 找不到 quick-adjust")
quick_end = quick + len('<div className="quick-adjust">')

modal_replacement = '''<span className="rule-tag">调整设计 · {editing.name}</span>
        <h3>告诉 AI 这次要改什么。</h3>
        <p>当前设计逻辑只在这里展开；右侧属性区保持简洁。</p>

        <div className="adjust-current-logic">
          <label>
            <span>方案概念</span>
            <input
              value={layouts[editing.id]?.concept||""}
              onChange={e=>setLayouts(prev=>({...prev,[editing.id]:{...prev[editing.id],concept:e.target.value}}))}
            />
          </label>
          <label>
            <span>当前设计说明</span>
            <textarea
              value={layouts[editing.id]?.rationale||""}
              onChange={e=>setLayouts(prev=>({...prev,[editing.id]:{...prev[editing.id],rationale:e.target.value}}))}
            />
          </label>
        </div>

        <div className="adjust-divider"><span>本次调整指令</span></div>
        <div className="quick-adjust">'''

s = s[:modal_start] + modal_replacement + s[quick_end:]
tsx.write_text(s, encoding="utf-8")

# 3) CSS
c = css.read_text(encoding="utf-8")

addon = r'''

/* v7.5.1 — guided inspector layout */
.result-meta{display:flex;flex-direction:column;padding:12px 14px!important}
.result-meta>b{font-size:13px;margin-bottom:7px}
.inspector-section{border-top:1px solid var(--line);padding:10px 0}
.inspector-section:first-of-type{margin-top:2px}
.inspector-section-title{margin-bottom:7px;font-size:9px;font-weight:700;letter-spacing:.02em;opacity:.48}
.inspector-grid{display:grid!important;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr) 66px;align-items:end;gap:6px}
.inspector-grid label{display:grid;grid-template-columns:12px minmax(0,1fr);align-items:center;gap:4px;font-size:8px;opacity:.68}
.inspector-grid input{min-width:0;width:100%}
.result-palette-editor{display:grid!important;grid-template-columns:1fr 1fr;gap:7px!important;margin:0!important}
.result-palette-editor label{display:grid!important;grid-template-columns:30px minmax(0,1fr);align-items:center;gap:5px!important}
.result-palette-editor select{width:100%;min-width:0!important}
.inspector-text-switch{justify-content:flex-start}
.inspector-text-switch button{flex:1}
.inspector-actions{display:grid;grid-template-columns:1fr 1fr;gap:6px}
.inspector-actions button{margin:0!important}
.inspector-actions .primary-adjust{grid-column:1/-1;min-height:34px;border-color:rgba(255,255,255,.22);font-weight:700}
.inspector-actions .danger-btn{opacity:.58}
.adjust-current-logic{display:grid;gap:10px;margin:14px 0}
.adjust-current-logic label{display:grid;gap:5px;font-size:9px;font-weight:700}
.adjust-current-logic input,.adjust-current-logic textarea{width:100%;box-sizing:border-box;border:1px solid var(--line);border-radius:7px;background:rgba(255,255,255,.035);color:inherit;padding:9px}
.adjust-current-logic textarea{min-height:86px;resize:vertical;line-height:1.55}
.adjust-divider{display:flex;align-items:center;gap:8px;margin:15px 0 10px;font-size:9px;opacity:.55}
.adjust-divider::after{content:"";height:1px;flex:1;background:var(--line)}
.editable-concept,.editable-rationale,.material-desc{display:none!important}
'''

if "v7.5.1 — guided inspector layout" not in c:
    c += addon

css.write_text(c, encoding="utf-8")

print("完成：")
print("✓ 使用稳定锚点修改，避免再次因为空行/格式变化匹配失败")
print("✓ 第四步右侧：画板 → 颜色 → 内容 → 快速操作")
print("✓ 方案概念 / 当前设计说明只在“调整设计”弹窗出现")
print("✓ 调整设计为主操作")
print("下一步：npm run build")
