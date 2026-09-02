import Whatsapp from "../../models/Whatsapp";
import { createCoexyChannel, getCoexyChannel } from "../../libs/coexy/coexy.service";
import { getIO } from "../../libs/socket";

interface Request {
  whatsappId: number;
  companyId: number;
}

const StartCoexySession = async ({ whatsappId, companyId }: Request): Promise<void> => {
  const whatsapp = await Whatsapp.findByPk(whatsappId);

  if (!whatsapp) {
    throw new Error("ERR_WAPP_NOT_FOUND");
  }

  // If already has a coexy channel, just refresh status
  if (whatsapp.coexy_channel_id) {
    try {
      const channel = await getCoexyChannel(whatsapp.coexy_channel_id);
      await whatsapp.update({
        coexy_status: channel.status,
        phone_number_id: channel.phone_number_id || whatsapp.phone_number_id,
        number: channel.display_phone_number || whatsapp.number,
        status: channel.status === "active" ? "CONNECTED" : "PENDING"
      });
    } catch (err) {
      console.log(`StartCoexySession: Error refreshing channel ${whatsapp.coexy_channel_id}: ${err.message}`);
    }
    return;
  }

  // Create new channel on Coexy
  const channel = await createCoexyChannel({ name: whatsapp.name });

  await whatsapp.update({
    coexy_channel_id: channel.id,
    coexy_channel_token: channel.channel_token,
    coexy_connect_url: channel.connect_url,
    coexy_status: channel.status,
    status: "PENDING"
  });

  const io = getIO();
  io.emit(`company-${companyId}-whatsapp`, {
    action: "update",
    whatsapp
  });
};

export default StartCoexySession;
