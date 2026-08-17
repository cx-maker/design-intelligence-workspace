import { references } from "@/mock/data";
import { AestheticReference, AestheticSearchService, SearchOptions } from "@/schemas/domain";

export class MockAestheticSearchService implements AestheticSearchService {
  async search(query: string, options?: SearchOptions): Promise<AestheticReference[]> {
    const needle = query.toLowerCase();
    const result = !needle ? references : references.filter((item) => `${item.title} ${item.tags.join(" ")}`.toLowerCase().includes(needle));
    return result.slice(0, options?.limit ?? result.length);
  }
}
