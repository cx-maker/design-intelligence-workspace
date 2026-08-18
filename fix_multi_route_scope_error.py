from pathlib import Path

p = Path.cwd() / "features/workspace/workspace-shell.tsx"
s = p.read_text(encoding="utf-8")

bad = '  const [activeStudyId,setActiveStudyId]=useState<string>(()=>keptStudies[0]?.id||selectedStudy?.id||"");\n  const activeStudy=keptStudies.find(x=>x.id===activeStudyId)||selectedStudy||keptStudies[0]||null;\n'
s = s.replace(bad, "")

start = s.find("function GenerateAndReview(")
if start == -1:
    raise SystemExit("[失败] 找不到 GenerateAndReview")

needle = '  const [error,setError]=useState("");'
pos = s.find(needle, start)
if pos == -1:
    raise SystemExit("[失败] 找不到 GenerateAndReview 内的 error state")

insert = '  const [error,setError]=useState("");\n  const [activeStudyId,setActiveStudyId]=useState<string>(()=>keptStudies[0]?.id||selectedStudy?.id||"");\n  const activeStudy=keptStudies.find((x:DeconstructionStudy)=>x.id===activeStudyId)||selectedStudy||keptStudies[0]||null;\n  useEffect(()=>{\n    if(!activeStudyId && (keptStudies[0]?.id||selectedStudy?.id)){\n      setActiveStudyId(keptStudies[0]?.id||selectedStudy?.id||"");\n    }\n  },[keptStudies,selectedStudy,activeStudyId]);'

s = s[:pos] + s[pos:].replace(needle, insert, 1)

p.write_text(s, encoding="utf-8")

print("完成：")
print("✓ 把 activeStudyId / activeStudy 从错误作用域移回 GenerateAndReview")
print("✓ 修复 keptStudies / selectedStudy / activeStudy / setActiveStudyId 的 TypeScript 未定义错误")
print("✓ 给 find 参数补充 DeconstructionStudy 类型")
print("下一步运行：npm run build")
