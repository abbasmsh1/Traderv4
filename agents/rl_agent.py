from .base_agent import BaseAgent
import os
import pandas as pd
import numpy as np


class RLForecastAgent(BaseAgent):
    def __init__(self, csv_path='market_data.csv'):
        # BaseAgent requires an api_key, but RL agent won't use LLM here
        super().__init__(api_key=None)
        self.system_message = None
        self.csv_path = csv_path
        self.model = None  # Lazy init

    def _ensure_model(self, input_dim):
        if self.model is not None:
            return
        try:
            # Lazy import to avoid heavy deps if unused
            from tensorflow import keras
            from tensorflow.keras import layers

            model = keras.Sequential([
                layers.Input(shape=(60, input_dim)),
                layers.LSTM(64, return_sequences=True),
                layers.Dropout(0.2),
                layers.LSTM(32),
                layers.Dense(16, activation='relu'),
                layers.Dense(1)
            ])
            model.compile(optimizer='adam', loss='mse')
            self.model = model
        except Exception as e:
            self.model = None

    def _prepare_sequences(self, df, feature_cols, window=60):
        data = df[feature_cols].values.astype(float)
        X, y = [], []
        for i in range(len(data) - window - 1):
            X.append(data[i:i+window])
            # Predict next close return
            next_close = df['close'].iloc[i+window]
            cur_close = df['close'].iloc[i+window-1]
            y.append((next_close - cur_close) / max(cur_close, 1e-6))
        return np.array(X), np.array(y)

    def _train_model(self, df):
        feature_cols = ['close', 'volume', 'RSI', 'SMA_20', 'SMA_50', 'MACD', 'MACD_SIGNAL', 'MACD_HIST']
        df = df.sort_values(['symbol', 'timestamp'])
        # Train per symbol and average weights (simple approach): use concatenated sequences
        frames = []
        for symbol, sdf in df.groupby('symbol'):
            if len(sdf) < 200:
                continue
            Xs, ys = self._prepare_sequences(sdf, feature_cols)
            if len(Xs) > 0:
                frames.append((Xs, ys))
        if not frames:
            return False

        input_dim = len(feature_cols)
        self._ensure_model(input_dim)
        if self.model is None:
            return False

        X = np.concatenate([f[0] for f in frames], axis=0)
        y = np.concatenate([f[1] for f in frames], axis=0)
        # Light training to avoid heavy compute
        try:
            self.model.fit(X, y, epochs=2, batch_size=64, verbose=0)
            return True
        except Exception:
            return False

    def _predict_direction(self, market_data, multi_pair):
        # Fallback: momentum on price_change_24h
        def fallback(md):
            change = float(md.get('price_change_24h', 0) or 0)
            if change > 0.5:
                return 'buy', 0.6
            if change < -0.5:
                return 'sell', 0.6
            return 'hold', 0.5

        # If no CSV or no model, use fallback
        if not os.path.exists(self.csv_path) or self.model is None:
            if multi_pair:
                out = {}
                for sym, md in market_data.items():
                    act, conf = fallback(md)
                    out[sym] = {'action': act, 'confidence': conf}
                return out
            act, conf = fallback(market_data)
            return {'action': act, 'confidence': conf}

        # With a trained model, use the latest window per symbol
        try:
            df = pd.read_csv(self.csv_path)
            df = df.dropna()
            feature_cols = ['close', 'volume', 'RSI', 'SMA_20', 'SMA_50', 'MACD', 'MACD_SIGNAL', 'MACD_HIST']
            if multi_pair:
                out = {}
                for sym, md in market_data.items():
                    sdf = df[df['symbol'] == sym].sort_values('timestamp')
                    if len(sdf) < 61:
                        act, conf = fallback(md)
                        out[sym] = {'action': act, 'confidence': conf}
                        continue
                    window = sdf[feature_cols].values[-60:]
                    window = np.expand_dims(window, axis=0)
                    pred = float(self.model.predict(window, verbose=0)[0][0])
                    if pred > 0:
                        out[sym] = {'action': 'buy', 'confidence': min(0.5 + abs(pred), 0.95)}
                    elif pred < 0:
                        out[sym] = {'action': 'sell', 'confidence': min(0.5 + abs(pred), 0.95)}
                    else:
                        out[sym] = {'action': 'hold', 'confidence': 0.5}
                return out
            # single pair
            sym = list(market_data.keys())[0] if isinstance(market_data, dict) and 'close' not in market_data else None
            if sym is None:
                # single symbol dict
                # no symbol label, just use fallback
                act, conf = fallback(market_data)
                return {'action': act, 'confidence': conf}
            sdf = df[df['symbol'] == sym].sort_values('timestamp')
            if len(sdf) < 61:
                act, conf = fallback(market_data[sym])
                return {'action': act, 'confidence': conf}
            window = sdf[feature_cols].values[-60:]
            window = np.expand_dims(window, axis=0)
            pred = float(self.model.predict(window, verbose=0)[0][0])
            if pred > 0:
                return {'action': 'buy', 'confidence': min(0.5 + abs(pred), 0.95)}
            if pred < 0:
                return {'action': 'sell', 'confidence': min(0.5 + abs(pred), 0.95)}
            return {'action': 'hold', 'confidence': 0.5}
        except Exception:
            # robust fallback
            if multi_pair:
                out = {}
                for sym, md in market_data.items():
                    act, conf = fallback(md)
                    out[sym] = {'action': act, 'confidence': conf}
                return out
            act, conf = fallback(market_data)
            return {'action': act, 'confidence': conf}

    def get_response(self, market_data, multi_pair=False):
        # Train model from CSV if possible (once per process)
        if self.model is None and os.path.exists(self.csv_path):
            try:
                df = pd.read_csv(self.csv_path)
                if not df.empty:
                    self._train_model(df)
            except Exception:
                pass

        forecast = self._predict_direction(market_data, multi_pair)
        if multi_pair:
            lines = ["=== RL LSTM Forecasts ==="]
            for sym, pred in forecast.items():
                lines.append(f"{sym}: {pred['action'].upper()} (confidence {pred['confidence']:.2f})")
            return "\n".join(lines)
        return f"RL Forecast: {forecast['action'].upper()} (confidence {forecast['confidence']:.2f})"


