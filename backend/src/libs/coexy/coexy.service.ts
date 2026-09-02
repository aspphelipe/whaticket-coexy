import axios, { AxiosInstance } from "axios";
import {
  ICoexyChannel,
  ICoexyChannelCreate,
  ICoexyWebhook,
  ICoexyWebhookCreate
} from "./ICoexy.interfaces";
import Setting from "../../models/Setting";

const COEXY_API_BASE = "https://api.coexy.com.br/functions/v1/api";
const COEXY_PROXY_BASE = "https://api.coexy.com.br/functions/v1/meta-proxy";

const getApiKey = async (): Promise<string> => {
  try {
    const setting = await Setting.findOne({
      where: { key: "coexyApiKey", companyId: 1 }
    });
    if (setting?.value) return setting.value;
  } catch (err) {
    console.log("getApiKey: fallback to env", err.message);
  }
  const key = process.env.COEXY_API_KEY;
  if (!key) throw new Error("COEXY_API_KEY não configurada. Configure em Configurações > Coexy ou na variável de ambiente COEXY_API_KEY.");
  return key;
};

const getClient = async (): Promise<AxiosInstance> => {
  const apiKey = await getApiKey();
  return axios.create({
    baseURL: COEXY_API_BASE,
    headers: {
      "x-api-key": apiKey,
      "Content-Type": "application/json"
    },
    timeout: 30000
  });
};

export const createCoexyChannel = async (
  data: ICoexyChannelCreate
): Promise<ICoexyChannel> => {
  const client = await getClient();
  const res = await client.post("/channels", data);
  return res.data;
};

export const getCoexyChannel = async (
  channelId: string
): Promise<ICoexyChannel> => {
  const client = await getClient();
  const res = await client.get(`/channels/${channelId}`);
  return res.data;
};

export const deleteCoexyChannel = async (
  channelId: string
): Promise<void> => {
  const client = await getClient();
  await client.delete(`/channels/${channelId}?force=true`);
};

export const listCoexyChannels = async (): Promise<ICoexyChannel[]> => {
  const client = await getClient();
  const res = await client.get("/channels");
  return res.data;
};

export const createCoexyWebhook = async (
  data: ICoexyWebhookCreate
): Promise<ICoexyWebhook> => {
  const client = await getClient();
  const res = await client.post("/webhooks", data);
  return res.data;
};

export const sendCoexyMessage = async (
  phoneNumberId: string,
  channelToken: string,
  payload: any
): Promise<any> => {
  const res = await axios.post(
    `${COEXY_PROXY_BASE}/${phoneNumberId}/messages`,
    payload,
    {
      headers: {
        Authorization: `Bearer ${channelToken}`,
        "Content-Type": "application/json"
      },
      timeout: 30000
    }
  );
  return res.data;
};

export const getCoexyHmacSecret = async (): Promise<string> => {
  try {
    const setting = await Setting.findOne({
      where: { key: "coexyHmacSecret", companyId: 1 }
    });
    if (setting?.value) return setting.value;
  } catch (err) {
    console.log("getCoexyHmacSecret: fallback to env", err.message);
  }
  return process.env.COEXY_HMAC_SECRET || "";
};
