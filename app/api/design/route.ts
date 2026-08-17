import { NextRequest, NextResponse } from "next/server";

const layoutItem = {
  type: "object",
  additionalProperties: false,
  required: ["materialId","concept","backgroundColor","logoScale","logoX","logoY","logoRotation","textPosition","textColor","rationale"],
  properties: {
    materialId:{type:"string"}, concept:{type:"string"}, backgroundColor:{type:"string"}, logoScale:{type:"number",minimum:0.6,maximum:5}, logoX:{type:"number",minimum:-20,maximum:120}, logoY:{type:"number",minimum:-20,maximum:120}, logoRotation:{type:"number",minimum:-45,maximum:45}, textPosition:{type:"string",enum:["top-left","top-right","bottom-left","bottom-right"]}, textColor:{type:"string"}, rationale:{type:"string"}
  }
};
export async function POST(req:NextRequest){
  try{
    const key=req.headers.get("x-openai-key"); if(!key) return NextResponse.json({error:"请先连接 OpenAI API Key"},{status:401});
    const body=await req.json(); const {mode,model="gpt-5.6",logoImage,materials=[],references=[],context,currentLayout,instruction}=body;
    if(mode==="test"){ const test=await fetch(`https://api.openai.com/v1/models/${encodeURIComponent(model)}`,{headers:{"Authorization":`Bearer ${key}`}}); const td=await test.json(); if(!test.ok) return NextResponse.json({error:td?.error?.message||"连接失败"},{status:test.status}); return NextResponse.json({ok:true,model:td.id}); }
    const prompt = mode==="adjust" ? `你是品牌视觉延展设计助手。只对当前方案做用户明确要求的局部调整，不推翻未被要求修改的结构。当前方案：${JSON.stringify(currentLayout)}。调整要求：${instruction}。品牌约束：${JSON.stringify(context)}。物料：${JSON.stringify(materials)}。` : `你是品牌视觉延展设计助手。根据已经确定的 Logo 和用户约束，为每个物料生成克制、现代、国际化的二维品牌版式参数。不要重新设计 Logo，只决定原始 Logo 的比例、位置、裁切感、背景和信息位置。品牌约束：${JSON.stringify(context)}。物料：${JSON.stringify(materials)}。参考图只用于感知调性、留白、密度和构图，不复制其中品牌元素。`;
    const content:any[]=[{type:"input_text",text:prompt}]; if(logoImage) content.push({type:"input_text",text:"下面是原始 Logo 图形预览："},{type:"input_image",image_url:logoImage,detail:"high"});
    for(const r of references){ if(r.image){ content.push({type:"input_text",text:`物料 ${r.id} 的用户参考图：`},{type:"input_image",image_url:r.image,detail:"high"}); } }
    const schema={type:"object",additionalProperties:false,required:["layouts"],properties:{layouts:{type:"array",minItems:materials.length,maxItems:materials.length,items:layoutItem}}};
    const openai=await fetch("https://api.openai.com/v1/responses",{method:"POST",headers:{"Authorization":`Bearer ${key}`,"Content-Type":"application/json"},body:JSON.stringify({model,store:false,input:[{role:"user",content}],text:{format:{type:"json_schema",name:"brand_layouts",strict:true,schema}}})});
    const data=await openai.json(); if(!openai.ok) return NextResponse.json({error:data?.error?.message||"OpenAI API 请求失败"},{status:openai.status});
    const text=data.output?.flatMap((x:any)=>x.content||[]).find((x:any)=>x.type==="output_text")?.text; if(!text) return NextResponse.json({error:"AI 没有返回可用版式"},{status:502});
    return NextResponse.json(JSON.parse(text));
  }catch(e){ return NextResponse.json({error:e instanceof Error?e.message:"服务端错误"},{status:500}); }
}
