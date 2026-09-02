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
    print("Connections/index.js Done")
else:
    print("Connections/index.js already patched")

# ============================================================
# Patch Options.js (Settings page) - Add Coexy API Key + HMAC Secret fields
# ============================================================
import os
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(p)))
opts_path = os.path.join(base_dir, "components", "Settings", "Options.js")

if not os.path.exists(opts_path):
    print("Options.js not found at", opts_path, "- skipping settings patch")
else:
    f=open(opts_path,"r");oc=f.read();f.close()
    opts_changed = False

    if "coexyApiKey" not in oc:
        # 1. Add state after metaRequireBusinessManagement
        sm = 'const [loadingMetaRequireBusinessManagement, setLoadingMetaRequireBusinessManagement] = useState(false);'
        if sm in oc:
            oc = oc.replace(sm, sm + '\n\n  // Coexy\n  const [coexyApiKey, setCoexyApiKey] = useState("");\n  const [loadingCoexyApiKey, setLoadingCoexyApiKey] = useState(false);\n  const [coexyHmacSecret, setCoexyHmacSecret] = useState("");\n  const [loadingCoexyHmacSecret, setLoadingCoexyHmacSecret] = useState(false);')
            print("Options.js: state inserted")
            opts_changed = True

        # 2. Add oldSettings parsing after aiSuggestionMessagesLimit block
        pm = re.search(r'(if \(aiSuggestionMessagesLimitPar\) \{[^}]+\})', oc)
        if pm:
            oc = oc[:pm.end()] + '\n\n      // Coexy\n      const coexyApiKeyPar = oldSettings.find(s => s.key === "coexyApiKey");\n      if (coexyApiKeyPar) setCoexyApiKey(coexyApiKeyPar.value);\n      const coexyHmacSecretPar = oldSettings.find(s => s.key === "coexyHmacSecret");\n      if (coexyHmacSecretPar) setCoexyHmacSecret(coexyHmacSecretPar.value);' + oc[pm.end():]
            print("Options.js: oldSettings parsing inserted")
            opts_changed = True

        # 3. Add handlers after handleAiApiKey
        hm = re.search(r'(async function handleAiApiKey\(value\) \{[\s\S]*?setLoadingAiApiKey\(false\);\s*\})', oc)
        if hm:
            oc = oc[:hm.end()] + '\n\n  async function handleCoexyApiKey(value) {\n    setCoexyApiKey(value);\n    setLoadingCoexyApiKey(true);\n    await updateUserCreation({ key: "coexyApiKey", value });\n    toast.success("Coexy API Key atualizada.");\n    setLoadingCoexyApiKey(false);\n  }\n\n  async function handleCoexyHmacSecret(value) {\n    setCoexyHmacSecret(value);\n    setLoadingCoexyHmacSecret(true);\n    await updateUserCreation({ key: "coexyHmacSecret", value });\n    toast.success("Coexy HMAC Secret atualizado.");\n    setLoadingCoexyHmacSecret(false);\n  }' + oc[hm.end():]
            print("Options.js: handlers inserted")
            opts_changed = True

        # 4. Add JSX after aiApiKey TextField block
        jm = re.search(r'(loadingAiApiKey\s*\?[\s\S]*?</FormHelperText>\s*</FormControl>\s*</Grid>)', oc)
        if jm:
            coexy_jsx = '\n\n          {/* Coexy - WhatsApp API */}\n          <Grid xs={12} item>\n            <Typography variant="subtitle1" style={{ fontWeight: 600, marginTop: 24, marginBottom: 8 }}>\n              Coexy - WhatsApp API\n            </Typography>\n          </Grid>\n\n          <Grid xs={12} md={6} item>\n            <FormControl className={classes.selectContainer}>\n              <TextField\n                id="coexyApiKey"\n                name="coexyApiKey"\n                type="password"\n                margin="dense"\n                label="Coexy API Key"\n                variant="outlined"\n                value={coexyApiKey}\n                onChange={(e) => setCoexyApiKey(e.target.value)}\n                onBlur={() => handleCoexyApiKey(coexyApiKey)}\n                InputLabelProps={{ shrink: true }}\n                placeholder="crt_pk_..."\n              />\n              <FormHelperText>\n                {loadingCoexyApiKey ? "Atualizando..." : "Coexy Dashboard > Configuracoes > API Keys"}\n              </FormHelperText>\n            </FormControl>\n          </Grid>\n\n          <Grid xs={12} md={6} item>\n            <FormControl className={classes.selectContainer}>\n              <TextField\n                id="coexyHmacSecret"\n                name="coexyHmacSecret"\n                type="password"\n                margin="dense"\n                label="Coexy HMAC Secret"\n                variant="outlined"\n                value={coexyHmacSecret}\n                onChange={(e) => setCoexyHmacSecret(e.target.value)}\n                onBlur={() => handleCoexyHmacSecret(coexyHmacSecret)}\n                InputLabelProps={{ shrink: true }}\n                placeholder="Retornado ao criar webhook"\n              />\n              <FormHelperText>\n                {loadingCoexyHmacSecret ? "Atualizando..." : "Retornado uma vez ao criar o webhook"}\n              </FormHelperText>\n            </FormControl>\n          </Grid>'
            oc = oc[:jm.end()] + coexy_jsx + oc[jm.end():]
            print("Options.js: JSX inserted")
            opts_changed = True

        if opts_changed:
            f=open(opts_path,"w");f.write(oc);f.close()
            print("Options.js Done")
        else:
            print("Options.js: could not find insertion points - manual edit needed")
    else:
        print("Options.js already has Coexy settings")
