import React, { useState, useContext } from "react";
import { toast } from "react-toastify";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  CircularProgress,
  Typography,
} from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";
import api from "../../services/api";
import toastError from "../../errors/toastError";
import QueueSelect from "../QueueSelect";
import { AuthContext } from "../../context/Auth/AuthContext";

const useStyles = makeStyles((theme) => ({
  root: {
    display: "flex",
    flexWrap: "wrap",
    gap: 16,
  },
  btnWrapper: {
    position: "relative",
    borderRadius: 10,
    textTransform: "none",
    fontWeight: 600,
    padding: "8px 28px",
    fontSize: "0.9rem",
  },
  buttonProgress: {
    color: "#6c5ce7",
    position: "absolute",
    top: "50%",
    left: "50%",
    marginTop: -12,
    marginLeft: -12,
  },
}));

const CoexyModal = ({ open, onClose }) => {
  const classes = useStyles();
  const { user } = useContext(AuthContext);
  const [name, setName] = useState("");
  const [selectedQueueIds, setSelectedQueueIds] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    if (!name.trim()) {
      toast.error("Informe um nome para a conexão");
      return;
    }

    setLoading(true);
    try {
      const { data } = await api.post("/whatsapp/", {
        name: name.trim(),
        channel: "whatsapp_coexy",
        queueIds: selectedQueueIds,
        isDefault: false,
      });

      toast.success("Conexão Coexy criada! Compartilhe o link de conexão.");
      onClose(data);
    } catch (err) {
      toastError(err);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setName("");
    setSelectedQueueIds([]);
    onClose(null);
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Typography variant="h6" style={{ fontWeight: 600 }}>
          Nova Conexão Coexy
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Conecte um número WhatsApp via Coexy
        </Typography>
      </DialogTitle>
      <DialogContent dividers>
        <div className={classes.root}>
          <TextField
            label="Nome da conexão"
            variant="outlined"
            fullWidth
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Ex: Suporte, Vendas..."
            autoFocus
          />
          <QueueSelect
            selectedQueueIds={selectedQueueIds}
            onChange={(values) => setSelectedQueueIds(values)}
          />
        </div>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Cancelar
        </Button>
        <Button
          onClick={handleSave}
          color="primary"
          variant="contained"
          disabled={loading}
          className={classes.btnWrapper}
        >
          Criar Conexão
          {loading && (
            <CircularProgress size={24} className={classes.buttonProgress} />
          )}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CoexyModal;
