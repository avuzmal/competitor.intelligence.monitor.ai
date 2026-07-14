export interface Client {
  id: number;
  name: string;
  email_address: string;
  is_active: boolean;
  stripe_customer_id?: string;
  slack_webhook_url?: string;
}

export interface Competitor {
  id: number;
  client_id: number;
  name: string;
  website_url: string;
  created_at: string;
}

export interface BriefingHistory {
  id: number;
  competitor_id: number;
  scrape_date: string;
  insight_json: CompetitorInsight;
  delivery_status: string;
}

export interface CompetitorInsight {
  threat_level: "LOW" | "MEDIUM" | "HIGH";
  executive_summary: string;
  what_changed: InsightSection[];
  what_it_means: InsightSection[];
  what_to_do: InsightSection[];
}

export interface InsightSection {
  category: string;
  description: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  client_id: number;
  name: string;
}
