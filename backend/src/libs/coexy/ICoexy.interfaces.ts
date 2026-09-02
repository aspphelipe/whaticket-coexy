export interface ICoexyChannel {
  id: string;
  name: string;
  status: "pending" | "active" | "disconnected" | "suspended";
  channel_token: string;
  connect_url: string;
  phone_number_id?: string;
  waba_id?: string;
  display_phone_number?: string;
  connected_at?: string;
  created_at: string;
}

export interface ICoexyChannelCreate {
  name: string;
}

export interface ICoexyWebhook {
  id: string;
  name: string;
  url: string;
  events: string[];
  status: "active" | "paused";
  hmac_secret?: string;
  created_at: string;
}

export interface ICoexyWebhookCreate {
  name: string;
  url: string;
  events: string[];
}

export interface ICoexyError {
  status: number;
  message: string;
}
