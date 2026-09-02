import React, { useState, useEffect, useCallback } from "react";
import { toast } from "react-toastify";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  CircularProgress,
  IconButton,
  Tooltip,
} from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";
import { FileCopy, CheckCircle, Link as LinkIcon } from "@material-ui/icons";
import api from "../../services/api";

const useStyles = makeStyles((theme) => ({
  statusContainer: {
    textAlign: "center",
    padding: theme.spacing(3),
  },
  connectUrl: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    padding: "12px 16px",
    background:
      theme.palette.type === "dark"
        ? "rgba(108, 92, 231, 0.1)"
        : "rgba(108, 92, 231, 0.05)",
    borderRadius: 12,
    border: "1px solid rgba(108, 92, 231, 0.3)",
    marginTop: 16,
    marginBottom: 16,
    wordBreak: "break-all",
  },
  statusDot: {
    width: 12,
    height: 12,
    borderRadius: "50%",
    display: "inline-block",
    marginRight: 8,
  },
  pendingDot: {
    backgroundColor: "#ffd93d",
    animation: "$pulse 2s infinite",
  },
  activeDot: {
    backgroundColor: "#00b894",
  },
  "@keyframes pulse": {
    "0%": { opacity: 1 },
    "50%": { opacity: 0.4 },
    "100%": { opacity: 1 },
  },
}));

const CoexyStatusModal = ({ open, onClose, whatsappId }) => {
  const classes = useStyles();
  const [status, setStatus] = useState("pending");
  const [connectUrl, setConnectUrl] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [copied, setCopied] = useState(false);

  const checkStatus = useCallback(async () => {
    if (!whatsappId) return;
    try {
      const { data } = await api.get(`/whatsapp/${whatsappId}/coexy-status`);
      setStatus(data.coexy_status);
      setConnectUrl(data.connect_url);
      if (data.display_phone_number) {
        setPhoneNumber(data.display_phone_number);
      }
      if (data.coexy_status === "active") {
        toast.success("Número conectado com sucesso!");
      }
    } catch (err) {
      console.error("Error checking coexy status:", err);
    }
  }, [whatsappId]);

  useEffect(() => {
    if (!open || !whatsappId) return;

    checkStatus();
    const interval = setInterval(checkStatus, 5000);
    return () => clearInterval(interval);
  }, [open, whatsappId, checkStatus]);

  const handleCopy = () => {
    navigator.clipboard.writeText(connectUrl);
    setCopied(true);
    toast.info("Link copiado!");
    setTimeout(() => setCopied(false), 2000);
  };

  const handleClose = () => {
    setStatus("pending");
    setConnectUrl("");
    setPhoneNumber("");
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Typography variant="h6" style={{ fontWeight: 600 }}>
          Conectar WhatsApp via Coexy
        </Typography>
      </DialogTitle>
      <DialogContent dividers>
        <div className={classes.statusContainer}>
          {status === "active" ? (
            <>
              <CheckCircle
                style={{ fontSize: 64, color: "#00b894", marginBottom: 16 }}
              />
              <Typography variant="h6" gutterBottom>
                Conectado!
              </Typography>
              {phoneNumber && (
                <Typography variant="body1" color="textSecondary">
                  Número: {phoneNumber}
                </Typography>
              )}
            </>
          ) : (
            <>
              <Box display="flex" alignItems="center" justifyContent="center" mb={2}>
                <span className={`${classes.statusDot} ${classes.pendingDot}`} />
                <Typography variant="body1">
                  Aguardando conexão do número...
                </Typography>
              </Box>
              <Typography
                variant="body2"
                color="textSecondary"
                style={{ marginBottom: 16 }}
              >
                Compartilhe o link abaixo com o dono do número WhatsApp.
                Ele deverá acessar o link e autorizar a conexão.
              </Typography>
              {connectUrl && (
                <div className={classes.connectUrl}>
                  <LinkIcon style={{ color: "#6c5ce7" }} />
                  <Typography
                    variant="body2"
                    style={{ flex: 1, textAlign: "left" }}
                  >
                    {connectUrl}
                  </Typography>
                  <Tooltip title={copied ? "Copiado!" : "Copiar link"}>
                    <IconButton size="small" onClick={handleCopy}>
                      <FileCopy fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </div>
              )}
              <CircularProgress
                size={20}
                style={{ color: "#6c5ce7", marginTop: 8 }}
              />
              <Typography variant="caption" display="block" color="textSecondary">
                Verificando automaticamente...
              </Typography>
            </>
          )}
        </div>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>
          {status === "active" ? "Fechar" : "Fechar e verificar depois"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CoexyStatusModal;
