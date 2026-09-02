import re, sys
p = sys.argv[1] if len(sys.argv) > 1 else "/home/deploy/empresa01/frontend/src/pages/Connections/index.js"
f=open(p,"r");c=f.read();f.close()

changed = False

# 1. Add useState
if "coexyModalOpen" not in c:
    c=c.replace("const [instagramProcessing, setInstagramProcessing] = useState(false);","const [instagramProcessing, setInstagramProcessing] = useState(false);\n  const [coexyModalOpen, setCoexyModalOpen] = useState(false);\n  const [coexyStatusOpen, setCoexyStatusOpen] = useState(false);\n  const [coexyWhatsappId, setCoexyWhatsappId] = useState(null);",1)
    print("useState inserted")
    changed = True

# 2. Add modals after WhatsAppModal
if "<CoexyModal" not in c:
    m=re.search(r"(<WhatsAppModal[\s\S]*?/>)",c)
    if m:
        c=c[:m.end()]+'\n      <CoexyModal\n        open={coexyModalOpen}\n        onClose={(whatsapp) => {\n          setCoexyModalOpen(false);\n          if (whatsapp) {\n            setCoexyWhatsappId(whatsapp.id);\n            setCoexyStatusOpen(true);\n          }\n        }}\n      />\n      <CoexyStatusModal\n        open={coexyStatusOpen}\n        onClose={() => setCoexyStatusOpen(false)}\n        whatsappId={coexyWhatsappId}\n      />'+c[m.end():]
        print("Modals inserted")
        changed = True

# 3. Add Coexy button
if "setCoexyModalOpen(true)" not in c:
    m2=re.search(r"(</MainHeaderButtonsWrapper>)",c)
    if m2:
        c=c[:m2.start()]+'\n              <Button\n                variant="contained"\n                style={{\n                  background: "linear-gradient(135deg, #6c5ce7, #a855f7)",\n                  color: "#fff",\n                  textTransform: "none",\n                  fontWeight: 600,\n                  borderRadius: 10,\n                  marginLeft: 8,\n                }}\n                onClick={() => setCoexyModalOpen(true)}\n              >\n                + Coexy\n              </Button>\n            '+c[m2.start():]
        print("Button inserted")
        changed = True

if changed:
    f=open(p,"w");f.write(c);f.close()
    print("Done")
else:
    print("Already patched, nothing to do")
