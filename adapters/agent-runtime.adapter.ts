import { AgentRun, AgentRuntime, AgentStatus, AgentTask } from "@/schemas/domain";

class MockRuntime implements AgentRuntime {
  async run(task: AgentTask): Promise<AgentRun> { void task; return { id: crypto.randomUUID(), status: "running" }; }
  async stop(runId: string): Promise<void> { void runId; }
  async getStatus(runId: string): Promise<AgentStatus> { void runId; return "completed"; }
}
export class CodexAdapter extends MockRuntime {}
export class ClaudeCodeAdapter extends MockRuntime {}
export class LocalAgentAdapter extends MockRuntime {}
