import { AestheticReference, DesignCandidate } from "@/schemas/domain";

export const references: AestheticReference[] = [
  { id: "r1", title: "未见之物", source: "品牌识别 / 2024", image: "https://images.unsplash.com/photo-1523726491678-bf852e717f6a?auto=format&fit=crop&w=900&q=80", tags: ["极简", "几何"] },
  { id: "r2", title: "Sundae School", source: "编辑设计 / 2024", image: "https://images.unsplash.com/photo-1545235617-9465d2a55698?auto=format&fit=crop&w=900&q=80", tags: ["大幅裁切", "高级"] },
  { id: "r3", title: "Aesop 研究", source: "包装 / 2023", image: "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?auto=format&fit=crop&w=900&q=80", tags: ["克制", "编辑感"] },
  { id: "r4", title: "动态形态", source: "活动视觉 / 2025", image: "https://images.unsplash.com/photo-1494438639946-1ebd1d20bf85?auto=format&fit=crop&w=900&q=80", tags: ["动态", "大胆"] },
];

export const candidates: DesignCandidate[] = [
  { id: "a", name: "A", description: "冷静而精确的视觉感受", color: "#008FDB" },
  { id: "b", name: "B", description: "具有编辑感的留白与光线", color: "#E4E5EA" },
  { id: "c", name: "C", description: "聚焦而有辨识度的几何语言", color: "#142A3A" },
];
