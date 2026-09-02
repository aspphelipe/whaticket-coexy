import sys
p = sys.argv[1] if len(sys.argv) > 1 else "/home/deploy/empresa01/backend/src/controllers/WhatsAppController.ts"
f=open(p,"r");c=f.read();f.close()
if "StartCoexySession" in c and "whatsapp_coexy" not in c:
    old = '  if (["whatsapp"].includes(whatsapp.channel)) {\n    StartWhatsAppSession(whatsapp, companyId);\n  }'
    new = '''  if (whatsapp.channel === "whatsapp_coexy") {
    try {
      await StartCoexySession({
        whatsappId: whatsapp.id,
        companyId: whatsapp.companyId
      });
      await whatsapp.reload();
    } catch (err) {
      console.log("store: Coexy session error:", err.message);
    }
  }

  if (["whatsapp"].includes(whatsapp.channel)) {
    StartWhatsAppSession(whatsapp, companyId);
  }'''
    c = c.replace(old, new, 1)
    f=open(p,"w");f.write(c);f.close()
    print("StartCoexySession block added to store method")
elif "whatsapp_coexy" in c:
    print("Already patched")
else:
    print("StartCoexySession import not found")
