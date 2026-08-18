from pathlib import Path

root = Path.cwd()
tsx = root / "features/workspace/workspace-shell.tsx"
api = root / "app/api/design/route.ts"

def rep(s, old, new, label):
    if old not in s:
        raise SystemExit(f"[失败] 找不到替换点：{label}")
    return s.replace(old, new, 1)

s = tsx.read_text(encoding="utf-8")

s = rep(
    s,
    'const c=document.createElement("canvas");c.width=1200;c.height=1200;',
    'const c=document.createElement("canvas");c.width=800;c.height=800;',
    "deconstruction canvas size"
)
s = rep(
    s,
    'const scale=Math.min(900/img.width,900/img.height);',
    'const scale=Math.min(620/img.width,620/img.height);',
    "deconstruction logo scale"
)
s = rep(
    s,
    'ctx.drawImage(img,(1200-w)/2,(1200-h)/2,w,h);',
    'ctx.drawImage(img,(800-w)/2,(800-h)/2,w,h);',
    "deconstruction canvas center"
)

old_block = '''      const r=await fetch("/api/design",{method:"POST",headers:{"Content-Type":"application/json","x-openai-key":api.key},body:JSON.stringify({
        mode:"deconstruct",model:api.model,provider:api.provider,baseUrl:api.baseUrl,apiMode:api.apiMode,
        logoImage,routes:route?[route]:[],selectedExtensions
      })});
      const d=await r.json();
      if(!r.ok)throw new Error(d.error||"解构失败");
      const studies=(d.studies||[]) as DeconstructionStudy[];
      setRouteStudies({[selectedRouteId]:studies});'''

new_block = '''      const allStudies:DeconstructionStudy[]=[];
      let partialError="";
      // 拆成 2 次较轻请求，每次只生成 2 个小样。
      // 蓝夜等中转层通常有自己的网关超时，单次“大图 + 4 个结构化方案”容易被 504 截断。
      for(let batchIndex=0;batchIndex<2;batchIndex++){
        try{
          const r=await fetch("/api/design",{method:"POST",headers:{"Content-Type":"application/json","x-openai-key":api.key},body:JSON.stringify({
            mode:"deconstruct",model:api.model,provider:api.provider,baseUrl:api.baseUrl,apiMode:api.apiMode,
            logoImage,routes:route?[route]:[],selectedExtensions,studyCount:2,batchIndex
          })});
          const d=await r.json();
          if(!r.ok)throw new Error(d.error||"解构失败");
          const batch=(d.studies||[]) as DeconstructionStudy[];
          allStudies.push(...batch.map((st,i)=>({...st,id:`${selectedRouteId}-${batchIndex}-${i}-${Date.now()}`})));
          setRouteStudies({[selectedRouteId]:[...allStudies]});
        }catch(e){
          partialError=e instanceof Error?e.message:"部分解构失败";
          if(!allStudies.length)throw e;
          break;
        }
      }
      if(partialError&&allStudies.length)setError(`已生成 ${allStudies.length} 个小样；后续一批未完成：${partialError}`);
      if(!allStudies.length)throw new Error("模型没有返回解构结果");'''

s = rep(s, old_block, new_block, "split deconstruction requests")
tsx.write_text(s, encoding="utf-8")

r = api.read_text(encoding="utf-8")

r = rep(
    r,
    'const {mode,model,provider="openai",baseUrl,apiMode="responses",logoImage,materials=[],references=[],context,currentLayout,instruction,routes=[],selectedExtensions=[]}=body;',
    'const {mode,model,provider="openai",baseUrl,apiMode="responses",logoImage,materials=[],references=[],context,currentLayout,instruction,routes=[],selectedExtensions=[],studyCount=4,batchIndex=0}=body;',
    "deconstruction request args"
)

r = rep(
    r,
    'const schema={type:"object",additionalProperties:false,required:["studies"],properties:{studies:{type:"array",minItems:routes.length*4,maxItems:routes.length*4,items:deconstructionStudyItem}}};',
    'const count=Math.max(1,Math.min(4,Number(studyCount)||2));const schema={type:"object",additionalProperties:false,required:["studies"],properties:{studies:{type:"array",minItems:count,maxItems:count,items:deconstructionStudyItem}}};',
    "dynamic deconstruction count"
)

r = rep(
    r,
    '当前只处理用户选中的一条路线，并生成 4 个明显不同的实验；elements',
    '当前只处理用户选中的一条路线，并生成 ${count} 个明显不同的实验；这是第 ${Number(batchIndex)+1} 批，请尽量避开常规居中、平均分布等已经容易想到的构图；elements',
    "deconstruction prompt count"
)

old_read = '''async function readResponse(r:Response){
  const raw=await r.text();
  if(!raw)return {};
  try{return JSON.parse(raw)}catch{return {raw:raw.slice(0,800)}}
}'''

new_read = '''async function readResponse(r:Response){
  const raw=await r.text();
  if(!raw)return {};
  try{return JSON.parse(raw)}catch{
    const compact=raw.replace(/<script[\\s\\S]*?<\\/script>/gi," ").replace(/<style[\\s\\S]*?<\\/style>/gi," ").replace(/<[^>]+>/g," ").replace(/\\s+/g," ").trim();
    if(r.status===504||/gateway timeout/i.test(compact))return {message:"中转服务网关超时（504）。这不是 API Key 失效；请求在第三方中转层等待模型返回时被截断。已改为更轻的分批生成，请重试。"};
    if(r.status>=500)return {message:`中转服务暂时异常 (${r.status})${compact?` · ${compact.slice(0,160)}`:""}`};
    return {raw:compact.slice(0,500)||raw.slice(0,500)};
  }
}'''

r = rep(r, old_read, new_read, "friendly gateway error")

api.write_text(r, encoding="utf-8")

print("完成：")
print("✓ 识别到截图是第三方中转层 504 Gateway Timeout，不再把整页 HTML 错误展示出来")
print("✓ Logo 分析预览从 1200px 降到 800px，降低请求体和视觉模型负担")
print("✓ 4 个解构小样拆成 2 批 × 2 个请求，降低单次网关超时概率")
print("✓ 第一批成功、第二批失败时保留已生成小样，不整轮作废")
print("✓ 504 会显示清楚的中文原因")
print("下一步运行：npm run build")
