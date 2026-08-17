export type WorkflowStep = "brand" | "references" | "generate" | "review" | "deliver";
export type QuickScore = "strong" | "like" | "neutral" | "reject";

export interface AestheticReference {
  id: string;
  title: string;
  source: string;
  image: string;
  tags: string[];
  score?: QuickScore;
  note?: string;
}

export interface DesignCandidate { id: string; name: string; description: string; color: string; }

export interface DesignDecision {
  id: string;
  projectId: string;
  selectedCandidateId: string;
  rejectedCandidateIds: string[];
  reasons: string[];
  note?: string;
  createdAt: string;
}

export interface SearchOptions { limit?: number; projectId?: string; }
export interface AestheticSearchService {
  search(query: string, options?: SearchOptions): Promise<AestheticReference[]>;
}

export interface AIProvider { id: string; name: string; status: "connected" | "not-configured" | "error"; vision?: boolean; image?: boolean; embedding?: boolean; reasoning?: boolean; }
export interface AgentTask { projectId: string; context: string; }
export interface AgentRun { id: string; status: AgentStatus; }
export type AgentStatus = "queued" | "running" | "completed" | "stopped";
export interface AgentRuntime { run(task: AgentTask): Promise<AgentRun>; stop(runId: string): Promise<void>; getStatus(runId: string): Promise<AgentStatus>; }
