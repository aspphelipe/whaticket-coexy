#!/usr/bin/env python3
"""
Patch script for Coexy module - handles complex JSX injections
Called by install.sh with the project directory as argument
"""
import re, sys, os

if len(sys.argv) < 2:
    print("Usage: python3 patch.py /path/to/project")
    sys.exit(1)

PROJECT_DIR = sys.argv[1]

def patch_file(path, label):
    if not os.path.exists(path):
        print(f"[WARN] {label}: file not found at {path}")
        return None
    f = open(path, "r"); c = f.read(); f.close()
    return c

def save_file(path, content, label):
    f = open(path, "w"); f.write(content); f.close()
    print(f"[OK]   {label}")

# ============================================================
# 1. WhatsAppController.ts - add imports at top
# ============================================================
wc_path = os.path.join(PROJECT_DIR, "backend/src/controllers/WhatsAppController.ts")
wc = patch_file(wc_path, "WhatsAppController.ts")
if wc and "StartCoexySession" not in wc:
    wc = 'import StartCoexySession from "../services/CoexyServices/StartCoexySession";\nimport { getCoexyChannel } from "../libs/coexy/coexy.service";\n' + wc
    save_file(wc_path, wc, "WhatsAppController.ts - imports coexy")
elif wc:
    print("[OK]   WhatsAppController.ts - imports already present")

# ============================================================
# 2. Connections/index.js - imports, useState, MenuItem, modals
# ============================================================
conn_path = os.path.join(PROJECT_DIR, "frontend/src/pages/Connections/index.js")
c = patch_file(conn_path, "Connections/index.js")
if c:
    changed = False

    # 2.1 Add imports
    if "CoexyModal" not in c:
        c = c.replace(
            'import PairingCodeModal from "../../components/PairingCodeModal";',
            'import PairingCodeModal from "../../components/PairingCodeModal";\nimport CoexyModal from "../../components/CoexyModal";\nimport CoexyStatusModal from "../../components/CoexyStatusModal";',
            1
        )
        # Fallback if PairingCodeModal not found
        if "CoexyModal" not in c:
            c = c.replace(
                'import QrcodeModal from "../../components/QrcodeModal";',
                'import QrcodeModal from "../../components/QrcodeModal";\nimport CoexyModal from "../../components/CoexyModal";\nimport CoexyStatusModal from "../../components/CoexyStatusModal";',
                1
            )
        print("[OK]   Connections - imports added")
        changed = True

    # 2.2 Add useState
    if "coexyModalOpen" not in c:
        c = c.replace(
            "const [instagramProcessing, setInstagramProcessing] = useState(false);",
            "const [instagramProcessing, setInstagramProcessing] = useState(false);\n  const [coexyModalOpen, setCoexyModalOpen] = useState(false);\n  const [coexyStatusOpen, setCoexyStatusOpen] = useState(false);\n  const [coexyWhatsappId, setCoexyWhatsappId] = useState(null);",
            1
        )
        print("[OK]   Connections - useState added")
        changed = True

    # 2.3 Add IconChannel case
    if 'case "whatsapp_coexy"' not in c:
        c = c.replace(
            'case "whatsapp_oficial":',
            'case "whatsapp_oficial":\n    case "whatsapp_coexy":',
            1
        )
        print("[OK]   Connections - IconChannel case added")
        changed = True

    # 2.4 Add coexyBadge style
    if "coexyBadge" not in c:
        c = c.replace(
            "officialBadge: {",
            'coexyBadge: {\n    background: "linear-gradient(135deg, #6c5ce7, #a855f7)",\n    color: "#fff",\n    fontSize: 10,\n    fontWeight: 700,\n    height: 22,\n  },\n  officialBadge: {',
            1
        )
        print("[OK]   Connections - coexyBadge style added")
        changed = True

    # 2.5 Remove standalone Coexy button if exists
    standalone_btn = re.search(r'\n\s*<Button\s*\n\s*variant="contained"\s*\n\s*style=\{\{\s*\n\s*background: "linear-gradient\(135deg, #6c5ce7, #a855f7\)"[\s\S]*?\+ Coexy\s*\n\s*</Button>', c)
    if standalone_btn:
        c = c[:standalone_btn.start()] + c[standalone_btn.end():]
        print("[OK]   Connections - standalone button removed")
        changed = True

    # 2.6 Add Coexy as MenuItem in PopupState menu
    if "setCoexyModalOpen" not in c:
        instagram_pattern = re.search(r'(: "Instagram"\}\s*</MenuItem>)', c)
        if instagram_pattern:
            coexy_menuitem = '\n\n                            <MenuItem\n                              onClick={() => {\n                                setCoexyModalOpen(true);\n                                popupState.close();\n                              }}\n                            >\n                              <WhatsApp\n                                fontSize="small"\n                                style={{\n                                  marginRight: "10px",\n                                  color: "#25D366",\n                                }}\n                              />\n                              Coexy - API Oficial\n                            </MenuItem>'
            pos = instagram_pattern.end()
            c = c[:pos] + coexy_menuitem + c[pos:]
            print("[OK]   Connections - Coexy MenuItem added")
            changed = True
        else:
            print("[WARN] Connections - Instagram MenuItem not found for insertion")

    # 2.7 Add CoexyModal and CoexyStatusModal rendering
    if "<CoexyModal" not in c:
        m = re.search(r'(<WhatsAppModal[\s\S]*?/>)', c)
        if m:
            modals = '\n      <CoexyModal\n        open={coexyModalOpen}\n        onClose={(whatsapp) => {\n          setCoexyModalOpen(false);\n          if (whatsapp) {\n            setCoexyWhatsappId(whatsapp.id);\n            setCoexyStatusOpen(true);\n          }\n        }}\n      />\n      <CoexyStatusModal\n        open={coexyStatusOpen}\n        onClose={() => setCoexyStatusOpen(false)}\n        whatsappId={coexyWhatsappId}\n      />'
            c = c[:m.end()] + modals + c[m.end():]
            print("[OK]   Connections - CoexyModal/CoexyStatusModal added")
            changed = True

    # 2.8 Add badge rendering for whatsapp_coexy
    if 'whatsApp.channel === "whatsapp_coexy"' not in c:
        badge_marker = re.search(r'(label="API OFICIAL"\s*/>)', c)
        if badge_marker:
            coexy_badge = '\n                              ) : whatsApp.channel === "whatsapp_coexy" ? (\n                                <Chip\n                                  className={classes.coexyBadge}\n                                  size="small"\n                                  label="COEXY"\n                                />'
            # Find the closing ternary after the official badge
            after_official = c[badge_marker.end():]
            # Look for the next ') :' which starts the next ternary branch
            next_ternary = re.search(r'(\s*\) : )', after_official)
            if next_ternary:
                insert_pos = badge_marker.end() + next_ternary.start()
                c = c[:insert_pos] + coexy_badge + c[insert_pos:]
                print("[OK]   Connections - Coexy badge rendering added")
                changed = True

    if changed:
        save_file(conn_path, c, "Connections/index.js - all patches applied")
    else:
        print("[OK]   Connections/index.js - already fully patched")

# ============================================================
# 3. Options.js - Coexy settings fields
# ============================================================
opts_path = os.path.join(PROJECT_DIR, "frontend/src/components/Settings/Options.js")
oc = patch_file(opts_path, "Options.js")
if oc and "coexyApiKey" not in oc:
    opts_changed = False

    # 3.0 Ensure Typography is imported
    if 'import { Typography }' not in oc:
        oc = oc.replace(
            'from "@material-ui/core/styles";',
            'from "@material-ui/core/styles";\nimport { Typography } from "@material-ui/core";',
            1
        )
        print("[OK]   Options.js - Typography imported")
        opts_changed = True

    # 3.1 Add state
    sm = 'const [loadingMetaRequireBusinessManagement, setLoadingMetaRequireBusinessManagement] = useState(false);'
    if sm in oc:
        oc = oc.replace(sm, sm + '\n\n  // Coexy\n  const [coexyApiKey, setCoexyApiKey] = useState("");\n  const [loadingCoexyApiKey, setLoadingCoexyApiKey] = useState(false);\n  const [coexyHmacSecret, setCoexyHmacSecret] = useState("");\n  const [loadingCoexyHmacSecret, setLoadingCoexyHmacSecret] = useState(false);')
        print("[OK]   Options.js - state added")
        opts_changed = True

    # 3.2 Add oldSettings parsing
    pm = re.search(r'(if \(aiSuggestionMessagesLimitPar\) \{[^}]+\})', oc)
    if pm:
        oc = oc[:pm.end()] + '\n\n      // Coexy\n      const coexyApiKeyPar = oldSettings.find(s => s.key === "coexyApiKey");\n      if (coexyApiKeyPar) setCoexyApiKey(coexyApiKeyPar.value);\n      const coexyHmacSecretPar = oldSettings.find(s => s.key === "coexyHmacSecret");\n      if (coexyHmacSecretPar) setCoexyHmacSecret(coexyHmacSecretPar.value);' + oc[pm.end():]
        print("[OK]   Options.js - oldSettings parsing added")
        opts_changed = True

    # 3.3 Add handlers
    hm = re.search(r'(async function handleAiApiKey\(value\) \{[\s\S]*?setLoadingAiApiKey\(false\);\s*\})', oc)
    if hm:
        oc = oc[:hm.end()] + '\n\n  async function handleCoexyApiKey(value) {\n    setCoexyApiKey(value);\n    setLoadingCoexyApiKey(true);\n    await updateUserCreation({ key: "coexyApiKey", value });\n    toast.success("Coexy API Key atualizada.");\n    setLoadingCoexyApiKey(false);\n  }\n\n  async function handleCoexyHmacSecret(value) {\n    setCoexyHmacSecret(value);\n    setLoadingCoexyHmacSecret(true);\n    await updateUserCreation({ key: "coexyHmacSecret", value });\n    toast.success("Coexy HMAC Secret atualizado.");\n    setLoadingCoexyHmacSecret(false);\n  }' + oc[hm.end():]
        print("[OK]   Options.js - handlers added")
        opts_changed = True

    # 3.4 Add JSX
    jm = re.search(r'(loadingAiApiKey\s*\?[\s\S]*?</FormHelperText>\s*</FormControl>\s*</Grid>)', oc)
    if jm:
        coexy_jsx = '\n\n          {/* Coexy - WhatsApp API */}\n          <Grid xs={12} item>\n            <Typography variant="subtitle1" style={{ fontWeight: 600, marginTop: 24, marginBottom: 8 }}>\n              Coexy - WhatsApp API\n            </Typography>\n          </Grid>\n\n          <Grid xs={12} md={6} item>\n            <FormControl className={classes.selectContainer}>\n              <TextField\n                id="coexyApiKey"\n                name="coexyApiKey"\n                type="password"\n                margin="dense"\n                label="Coexy API Key"\n                variant="outlined"\n                value={coexyApiKey}\n                onChange={(e) => setCoexyApiKey(e.target.value)}\n                onBlur={() => handleCoexyApiKey(coexyApiKey)}\n                InputLabelProps={{ shrink: true }}\n                placeholder="crt_pk_..."\n              />\n              <FormHelperText>\n                {loadingCoexyApiKey ? "Atualizando..." : "Coexy Dashboard > Configuracoes > API Keys"}\n              </FormHelperText>\n            </FormControl>\n          </Grid>\n\n          <Grid xs={12} md={6} item>\n            <FormControl className={classes.selectContainer}>\n              <TextField\n                id="coexyHmacSecret"\n                name="coexyHmacSecret"\n                type="password"\n                margin="dense"\n                label="Coexy HMAC Secret"\n                variant="outlined"\n                value={coexyHmacSecret}\n                onChange={(e) => setCoexyHmacSecret(e.target.value)}\n                onBlur={() => handleCoexyHmacSecret(coexyHmacSecret)}\n                InputLabelProps={{ shrink: true }}\n                placeholder="Retornado ao criar webhook"\n              />\n              <FormHelperText>\n                {loadingCoexyHmacSecret ? "Atualizando..." : "Retornado uma vez ao criar o webhook"}\n              </FormHelperText>\n            </FormControl>\n          </Grid>'
        oc = oc[:jm.end()] + coexy_jsx + oc[jm.end():]
        print("[OK]   Options.js - JSX added")
        opts_changed = True

    if opts_changed:
        save_file(opts_path, oc, "Options.js - all patches applied")
    else:
        print("[WARN] Options.js - insertion points not found, manual edit needed")
elif oc:
    print("[OK]   Options.js - already has Coexy settings")

print("\n[DONE] All frontend patches complete.")
