import re, sys
p = sys.argv[1] if len(sys.argv) > 1 else "/home/deploy/empresa01/frontend/src/pages/Connections/index.js"
f=open(p,"r");c=f.read();f.close()

changed = False

# 1. Add useState (if not present)
if "coexyModalOpen" not in c:
    c=c.replace("const [instagramProcessing, setInstagramProcessing] = useState(false);","const [instagramProcessing, setInstagramProcessing] = useState(false);\n  const [coexyModalOpen, setCoexyModalOpen] = useState(false);\n  const [coexyStatusOpen, setCoexyStatusOpen] = useState(false);\n  const [coexyWhatsappId, setCoexyWhatsappId] = useState(null);",1)
    print("useState inserted")
    changed = True

# 2. Add modals after WhatsAppModal (if not present)
if "<CoexyModal" not in c:
    m=re.search(r"(<WhatsAppModal[\s\S]*?/>)",c)
    if m:
        c=c[:m.end()]+'\n      <CoexyModal\n        open={coexyModalOpen}\n        onClose={(whatsapp) => {\n          setCoexyModalOpen(false);\n          if (whatsapp) {\n            setCoexyWhatsappId(whatsapp.id);\n            setCoexyStatusOpen(true);\n          }\n        }}\n      />\n      <CoexyStatusModal\n        open={coexyStatusOpen}\n        onClose={() => setCoexyStatusOpen(false)}\n        whatsappId={coexyWhatsappId}\n      />'+c[m.end():]
        print("Modals inserted")
        changed = True

# 3. Remove standalone Coexy button (if exists from previous fix)
standalone_btn = re.search(r'\n\s*<Button\s*\n\s*variant="contained"\s*\n\s*style=\{\{\s*\n\s*background: "linear-gradient\(135deg, #6c5ce7, #a855f7\)"[\s\S]*?\+ Coexy\s*\n\s*</Button>', c)
if standalone_btn:
    c = c[:standalone_btn.start()] + c[standalone_btn.end():]
    print("Standalone button removed")
    changed = True

# 4. Add Coexy as MenuItem inside PopupState menu (after Instagram MenuItem)
if "setCoexyModalOpen" not in c or standalone_btn:
    # Find the Instagram MenuItem closing tag pattern and insert after it
    instagram_pattern = re.search(r'(: "Instagram"\}\s*</MenuItem>)', c)
    if instagram_pattern:
        coexy_menuitem = '''

                            <MenuItem
                              onClick={() => {
                                setCoexyModalOpen(true);
                                popupState.close();
                              }}
                            >
                              <WhatsApp
                                fontSize="small"
                                style={{
                                  marginRight: "10px",
                                  color: "#25D366",
                                }}
                              />
                              Coexy - API Oficial
                            </MenuItem>'''
        insert_pos = instagram_pattern.end()
        c = c[:insert_pos] + coexy_menuitem + c[insert_pos:]
        print("Coexy MenuItem inserted in menu")
        changed = True
    else:
        print("Could not find Instagram MenuItem to insert after")

if changed:
    f=open(p,"w");f.write(c);f.close()
    print("Done")
else:
    print("Already patched, nothing to do")
