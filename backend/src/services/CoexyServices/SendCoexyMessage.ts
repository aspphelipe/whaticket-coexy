import axios from "axios";
import fs from "fs";
import mime from "mime-types";
import FormData from "form-data";

const urlApi = process.env.URL_API_OFICIAL;
const tokenApi = process.env.TOKEN_API_OFICIAL;

interface ISendCoexyMessageData {
  type: string;
  to: string;
  text?: { body: string };
  reaction?: any;
  audio?: any;
  document?: any;
  image?: any;
  sticker?: any;
  video?: any;
  location?: any;
  contacts?: any;
  interactive?: any;
  template?: any;
}

export const sendMessageCoexy = async (
  filePath: string | null,
  token: string,
  data: ISendCoexyMessageData
): Promise<any> => {
  const formData = new FormData();

  if (filePath && fs.existsSync(filePath)) {
    const fileStream = fs.createReadStream(filePath);
    const mimeType = mime.lookup(filePath) || "application/octet-stream";
    const fileName = filePath.split("/").pop() || "file";
    formData.append("file", fileStream, {
      filename: fileName,
      contentType: mimeType
    });
  }

  formData.append("data", JSON.stringify(data));

  const res = await axios.post(
    `${urlApi}/v1/send-message-coexy/${token}`,
    formData,
    {
      headers: {
        ...formData.getHeaders(),
        Authorization: `Bearer ${tokenApi}`
      },
      timeout: 60000
    }
  );

  if (res.status === 200 || res.status === 201) {
    return res.data;
  }

  throw new Error(`Mensagem não enviada via Coexy: ${JSON.stringify(res.data)}`);
};

export default sendMessageCoexy;
