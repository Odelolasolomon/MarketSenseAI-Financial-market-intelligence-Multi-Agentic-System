"""
Price Prediction Model (pretrained)
"""
from typing import Optional, List
import numpy as np
import torch
from transformers import AutoModelForSequenceClassification
from src.utilities.logger import get_logger

logger = get_logger(__name__)


class PricePredictor:
    """ML model using a pretrained financial LSTM"""

    def __init__(self):
        try:
            # Load pretrained LSTM model from HuggingFace
            self.model = AutoModelForSequenceClassification.from_pretrained(
                "borisbanushev/stock-prediction-lstm"
            )
            self.model.eval()  # inference mode
            logger.info("Loaded pretrained LSTM price prediction model.")
        except Exception as e:
            logger.error(f"Failed to load pretrained model: {e}")
            self.model = None

    def predict_next_price(
        self,
        historical_prices: List[float],
        horizon: int = 1
    ) -> Optional[float]:

        if not historical_prices:
            return None

        # If model failed to load → fallback to moving average
        if self.model is None:
            logger.warning("Using fallback moving average model.")
            return float(np.mean(historical_prices[-10:]))

        try:
            # Convert historical prices into tensor
            seq = torch.tensor(historical_prices[-50:], dtype=torch.float32)
            seq = seq.unsqueeze(0).unsqueeze(-1)  # shape: (1, seq_len, 1)

            with torch.no_grad():
                output = self.model(seq)
                pred = output.logits.squeeze().item()

            return float(pred)

        except Exception as e:
            logger.error(f"Error predicting price: {e}")
            return float(np.mean(historical_prices[-10:]))

    def predict_trend(self, historical_prices: List[float]) -> str:
        """Predict bullish / bearish / neutral trend"""

        if len(historical_prices) < 2:
            return "neutral"

        recent_avg = np.mean(historical_prices[-5:])
        older_avg = np.mean(historical_prices[-10:-5])

        if recent_avg > older_avg * 1.02:
            return "bullish"
        elif recent_avg < older_avg * 0.98:
            return "bearish"
        return "neutral"
