CREATE TABLE "coexyConnection" (
    "id" SERIAL NOT NULL,
    "create_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "update_at" TIMESTAMP(3),
    "deleted_at" TIMESTAMP(3),
    "phone_number_id" TEXT NOT NULL,
    "channel_token" TEXT NOT NULL,
    "coexy_channel_id" TEXT NOT NULL,
    "companyId" INTEGER NOT NULL,
    "whatsappId" INTEGER NOT NULL,
    "token_mult100" TEXT NOT NULL,
    "use_rabbitmq" BOOLEAN NOT NULL DEFAULT true,

    CONSTRAINT "coexyConnection_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX "coexyConnection_phone_number_id_key" ON "coexyConnection"("phone_number_id");
CREATE UNIQUE INDEX "coexyConnection_coexy_channel_id_key" ON "coexyConnection"("coexy_channel_id");
CREATE UNIQUE INDEX "coexyConnection_token_mult100_key" ON "coexyConnection"("token_mult100");
