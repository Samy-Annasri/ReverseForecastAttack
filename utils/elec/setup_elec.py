import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset

def prepare_electric_dataset(
    serie,
    sequence_length=30,
    batch_size=64,
    split_ratio=0.8,
    reverse=False
):
    serie = np.array(serie)

    serie_min = np.min(serie)
    serie_max = np.max(serie)
    serie_norm = (serie - serie_min) / (serie_max - serie_min)

    X, Y, used_dates = [], [], []

    if not reverse:
        for i in range(len(serie_norm) - sequence_length):
            X.append(serie_norm[i:i + sequence_length])
            Y.append(serie_norm[i + sequence_length])
            used_dates.append(i + sequence_length)
    else:
        for i in range(sequence_length, len(serie_norm)):
            seq = serie_norm[i-sequence_length:i][::-1]
            target_idx = i - sequence_length - 1
            if target_idx >= 0:
                X.append(seq)
                Y.append(serie_norm[target_idx])
                used_dates.append(target_idx)

    X = np.array(X)
    Y = np.array(Y)

    split = int(len(X) * split_ratio)
    X_train, X_test = X[:split], X[split:]
    Y_train, Y_test = Y[:split], Y[split:]

    dates_train = used_dates[:split]
    dates_test = used_dates[split:]

    X_train = torch.tensor(X_train, dtype=torch.float32).unsqueeze(-1)
    Y_train = torch.tensor(Y_train, dtype=torch.float32).unsqueeze(-1)
    X_test = torch.tensor(X_test, dtype=torch.float32).unsqueeze(-1)
    Y_test = torch.tensor(Y_test, dtype=torch.float32).unsqueeze(-1)

    train_loader = DataLoader(TensorDataset(X_train, Y_train), batch_size=batch_size, shuffle=True, drop_last=True)
    test_loader = DataLoader(TensorDataset(X_test, Y_test), batch_size=batch_size, drop_last=True)

    return {
        'train_loader': train_loader,
        'test_loader': test_loader,
        'train_size': len(X_train),
        'test_size': len(X_test),
        'min_max': (serie_min, serie_max),
        'dates': dates_train + dates_test,
        'X': torch.tensor(X, dtype=torch.float32).unsqueeze(-1),
        'Y': torch.tensor(Y, dtype=torch.float32).unsqueeze(-1)
    }
