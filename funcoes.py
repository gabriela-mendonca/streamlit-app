# Bibliotecas principais
import numpy as np
import pandas as pd

import scipy.stats as stats
# from scipy import stats
from scipy.stats import norm

from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportions_ztest

import math
from math import ceil

# Definição das funções de tamanho e duração da amostra

def calcular_tamanho_amostra(
    tx_conversao,           # taxa de respondentes promotores+detratores
    mde=0.05,               # diferença mínima detectável
    alpha=0.05,
    power=0.90
):
    """
    Calcula tamanho de amostra necessário para teste A/B (duas proporções) considerando todos respondentes válidos (promotores + detratores)
        media_amostras_dia: número médio de amostras por dia
        tx_conversao: taxa de conversão atual  (ex: 0.10)
        mde: efeito mínimo detectável (diferença absoluta, ex: 0.05)
        alpha: nível de significância
        power: poder estatístico

    Retorna:
        - amostra por grupo
    """
    
    # Z-scores
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    
    # expected_conversion = tx_conversao * (1 + mde)
    # p1 = np.sqrt(tx_conversao * (1 - tx_conversao))
    # p2 = np.sqrt(expected_conversion * (1 - expected_conversion))

    p1 = tx_conversao
    p2 = tx_conversao * (1 + mde)
    
    # proporção média
    p_bar = (p1 + p2) / 2

    # fórmula clássica para duas proporções
    numerador = (z_alpha * math.sqrt(2 * p_bar * (1 - p_bar)) +
                 z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
                ) ** 2
    denominador = (p2 - p1) ** 2
    
    amostra_grupo = numerador / denominador

    return int(amostra_grupo)
    
def calcular_duracao_dias(amostra_grupo, media_amostras_dia, traffic_allocation=1):
    """
    Calcula tempo necessário para teste A/B (duas proporções) atingir significância estatística considerando o tamanho de amostra necessário e a média de amostras por dia.
        amostra_grupo: tamanho de amostra necessário por grupo (retorno da função calcular_tamanho_amostra)
        media_amostras_dia: número médio de amostras por dia
        traffic_allocation: proporção de tráfego alocada para o teste (ex: 0.5 para 50% do tráfego)

    Retorna:
        - tempo estimado em dias
    """
    # tempo estimado em dias
    amostras_dia_grupo = (media_amostras_dia * traffic_allocation) / 2     # considerando divisão igual entre os grupos (50|50)
    dias_necessarios = np.ceil(amostra_grupo / amostras_dia_grupo)
    return int(dias_necessarios)


def teste_ab_proporcao(controle_total, controle_conversao, alternativa_total, alternativa_conversao, alpha=0.05):
    """
    Teste Z para duas proporções
    """
    
    p1 = controle_conversao / controle_total
    p2 = alternativa_conversao / alternativa_total
    
    p_pool = (controle_conversao + alternativa_conversao) / (controle_total + alternativa_total)
    
    # Calculate absolute and relative differences
    absolute_diff = p2 - p1
    relative_diff = absolute_diff / p1
    
    # Calculate z-score
    se = math.sqrt(p_pool * (1 - p_pool) * (1/controle_total + 1/alternativa_total))
    z_score = absolute_diff / se
    
    # # Calculate standard errors
    # control_se = p1 * (1 - p1) / controle_total
    # treatment_se = p2 * (1 - p2) / alternativa_total
    # # Calculate z-score
    # pooled_se = np.sqrt(control_se + treatment_se)
    # z_score = absolute_diff / pooled_se

    # Calculate p-value (two-tailed test)
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
    # Determine if result is statistically significant
    is_significant = p_value < alpha
    
    # Calculate confidence interval
    z_critical = stats.norm.ppf(1 - alpha/2)
    margin_of_error = z_critical * se
    ci_lower = absolute_diff - margin_of_error
    ci_upper = absolute_diff + margin_of_error
    
    return {
        "Tx. conversão do controle": p1,
        "Tx. conversão do alternativa": p2,
        'Dif. absoluta (%)': absolute_diff,
        'Dif. relativa (%)': relative_diff * 100,  # Convert to percentage
        "z_score": z_score,
        "p_value": p_value,
        'IC_inferior': ci_lower,
        'IC_superior': ci_upper,
        "Significativo": is_significant
    }

def calcular_poder_atual(p1, p2, controle_total, alternativa_total, alpha=0.05):
    """
    Estima poder atual do teste
    """
    
    effect_size = abs(p2 - p1)
    p_pool = (p1 + p2) / 2
    se = math.sqrt(p_pool * (1 - p_pool) * (1/controle_total + 1/alternativa_total))
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z = effect_size / se
    power = stats.norm.cdf(z - z_alpha)
    
    return power


def bayesian_ab_test(controle_total, controle_conversao, alternativa_total, alternativa_conversao, samples=100000):
    """
    Simulação Bayesiana com Beta-Binomial
    """
    
    # prior não informativa
    alpha_prior = 1
    beta_prior = 1
    
    # posterior
    alpha_c = alpha_prior + controle_conversao
    beta_c = beta_prior + (controle_total - controle_conversao)
    
    alpha_v = alpha_prior + alternativa_conversao
    beta_v = beta_prior + (alternativa_total - alternativa_conversao)
    
    # amostragem
    samples_c = np.random.beta(alpha_c, beta_c, samples)
    samples_v = np.random.beta(alpha_v, beta_v, samples)
    
    prob_v_better = np.mean(samples_v > samples_c)
    
    lift = np.mean(samples_v - samples_c)
    
    return {
        "prob_variant_better": prob_v_better,
        "expected_lift": lift
    }