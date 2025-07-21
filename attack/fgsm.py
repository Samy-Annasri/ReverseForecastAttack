import torch
import numpy as np

def fgsm_attack(model, data_loader, loss_fn, epsilon, price_min, price_max):
    model.eval()
    device = next(model.parameters()).device
    adv_predictions = []
    true_values = []

    for x, y in data_loader:
        x = x.to(device).clone().detach().requires_grad_(True)
        y = y.to(device).clone().detach()

        model.train()
        # Forward pass
        output = model(x)
        loss = loss_fn(output, y)

        # Backward pass
        model.zero_grad()
        loss.backward()

        model.eval()

        # FGSM perturbation
        data_grad = x.grad.data
        sign_data_grad = data_grad.sign()
        perturbed_x = x + epsilon * sign_data_grad
        perturbed_x = torch.clamp(perturbed_x, 0, 1)

        # Predict with perturbed input
        with torch.no_grad():
            adv_output = model(perturbed_x)

        adv_predictions.extend(adv_output.squeeze().detach().cpu().numpy())
        true_values.extend(y.squeeze().detach().cpu().numpy())

    # Denormalize
    adv_predictions = np.array(adv_predictions) * (price_max - price_min) + price_min
    true_values = np.array(true_values) * (price_max - price_min) + price_min

    return true_values, adv_predictions
