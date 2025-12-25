#!/usr/bin/env python3
"""
Script para recalcular os valores de métricas do CloudWatch:
- CPU e Memory: Máximo absoluto entre todos os valores de todos os runs
- Network: Média dos valores máximos de cada run
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any

# Tipos de teste
TEST_TYPES = [
    "grpc:average_load",
    "grpc:high_load",
    "grpc:spike",
    "grpc:breakpoint",
    "rest:average_load",
    "rest:high_load",
    "rest:spike",
    "rest:breakpoint"
]

# Serviços
SERVICES = ["order", "payment", "product", "user"]

# Métricas a recalcular
METRICS = ["cpu", "memory", "network_rx", "network_tx"]


def get_maximum_value_from_file(file_path: str) -> float:
    """
    Extrai o valor máximo de um arquivo de métricas do CloudWatch
    
    Args:
        file_path: Caminho para o arquivo JSON de métricas
        
    Returns:
        Valor máximo encontrado no arquivo, ou 0.0 se não encontrar
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if 'Datapoints' not in data:
            return 0.0
        
        max_values = []
        for datapoint in data['Datapoints']:
            if 'Maximum' in datapoint:
                max_values.append(datapoint['Maximum'])
        
        if not max_values:
            return 0.0
        
        # Retorna o máximo entre todos os datapoints
        return max(max_values)
    
    except Exception as e:
        print(f"Erro ao processar {file_path}: {e}")
        return 0.0


def calculate_metric_value(test_type: str, service: str, metric_type: str) -> Dict[str, Any]:
    """
    Calcula o valor da métrica para um serviço específico.
    Para CPU e Memory: retorna o máximo absoluto entre todos os runs.
    Para Network: retorna a média dos máximos de cada run.
    
    Args:
        test_type: Tipo de teste (ex: "grpc:average_load")
        service: Nome do serviço (ex: "order")
        metric_type: Tipo de métrica (ex: "cpu", "memory", "network_rx", "network_tx")
        
    Returns:
        Dicionário com average_maximum, total_files_processed e unit
    """
    test_results_dir = Path("test-results") / test_type / service
    
    if not test_results_dir.exists():
        print(f"Diretório não encontrado: {test_results_dir}")
        return None
    
    # Encontrar todos os arquivos de métricas do tipo especificado
    metric_files = []
    for run_num in range(1, 6):  # Assumindo runs de 1 a 5
        if metric_type == "cpu":
            file_name = f"run_{run_num}_{service}_cpu_metrics.json"
        elif metric_type == "memory":
            file_name = f"run_{run_num}_{service}_memory_metrics.json"
        elif metric_type == "network_rx":
            file_name = f"run_{run_num}_{service}_network_rx_bytes_metrics.json"
        elif metric_type == "network_tx":
            file_name = f"run_{run_num}_{service}_network_tx_bytes_metrics.json"
        else:
            continue
        
        file_path = test_results_dir / file_name
        if file_path.exists():
            metric_files.append(file_path)
    
    if not metric_files:
        print(f"Nenhum arquivo encontrado para {test_type}/{service}/{metric_type}")
        return None
    
    # Extrair o valor máximo de cada arquivo
    maximum_values = []
    for file_path in metric_files:
        max_value = get_maximum_value_from_file(str(file_path))
        if max_value > 0:
            maximum_values.append(max_value)
            print(f"  {file_path.name}: máximo = {max_value:.2f}")
    
    if not maximum_values:
        return None
    
    # Para CPU e Memory: usar o máximo absoluto
    # Para Network: usar a média dos máximos
    if metric_type in ["cpu", "memory"]:
        final_value = max(maximum_values)
        print(f"  → Máximo absoluto: {final_value:.2f}")
    else:
        final_value = sum(maximum_values) / len(maximum_values)
        print(f"  → Média dos máximos: {final_value:.2f}")
    
    # Determinar a unidade
    if metric_type in ["cpu", "memory"]:
        unit = "Percent"
    else:
        unit = "Bytes"
    
    return {
        "average_maximum": final_value,
        "total_files_processed": len(maximum_values),
        "unit": unit
    }


def update_final_results(test_type: str, service: str):
    """
    Atualiza o arquivo cloudwatch_metrics.json em final_results com os valores recalculados
    
    Args:
        test_type: Tipo de teste
        service: Nome do serviço
    """
    final_results_file = Path("final_results") / test_type / service / "cloudwatch_metrics.json"
    
    if not final_results_file.exists():
        print(f"Arquivo não encontrado: {final_results_file}")
        return
    
    # Ler o arquivo existente
    try:
        with open(final_results_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Erro ao ler {final_results_file}: {e}")
        return
    
    print(f"\n=== Processando {test_type}/{service} ===")
    
    # Recalcular cada métrica
    if "cpu_utilization" in data:
        cpu_result = calculate_metric_value(test_type, service, "cpu")
        if cpu_result:
            data["cpu_utilization"] = cpu_result
            print(f"CPU: {cpu_result['average_maximum']:.2f}% (máximo absoluto de {cpu_result['total_files_processed']} arquivos)")
    
    if "memory_utilization" in data:
        memory_result = calculate_metric_value(test_type, service, "memory")
        if memory_result:
            data["memory_utilization"] = memory_result
            print(f"Memory: {memory_result['average_maximum']:.2f}% (máximo absoluto de {memory_result['total_files_processed']} arquivos)")
    
    if "network_rx_bytes" in data:
        network_rx_result = calculate_metric_value(test_type, service, "network_rx")
        if network_rx_result:
            data["network_rx_bytes"] = network_rx_result
            print(f"Network RX: {network_rx_result['average_maximum']:.2f} bytes (média de {network_rx_result['total_files_processed']} arquivos)")
    
    if "network_tx_bytes" in data:
        network_tx_result = calculate_metric_value(test_type, service, "network_tx")
        if network_tx_result:
            data["network_tx_bytes"] = network_tx_result
            print(f"Network TX: {network_tx_result['average_maximum']:.2f} bytes (média de {network_tx_result['total_files_processed']} arquivos)")
    
    # Salvar o arquivo atualizado
    try:
        with open(final_results_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✓ Arquivo atualizado: {final_results_file}\n")
    except Exception as e:
        print(f"Erro ao salvar {final_results_file}: {e}\n")


def main():
    """
    Processa todos os tipos de teste e serviços
    """
    print("=" * 60)
    print("RECALCULANDO VALORES DE CPU, MEMORY E NETWORK")
    print("CPU e Memory: Máximo absoluto entre todos os runs")
    print("Network: Média dos máximos de cada run")
    print("=" * 60)
    
    total_processed = 0
    total_updated = 0
    
    for test_type in TEST_TYPES:
        for service in SERVICES:
            final_results_file = Path("final_results") / test_type / service / "cloudwatch_metrics.json"
            
            if final_results_file.exists():
                total_processed += 1
                update_final_results(test_type, service)
                total_updated += 1
            else:
                print(f"Arquivo não encontrado: {final_results_file}")
    
    print("=" * 60)
    print(f"PROCESSAMENTO CONCLUÍDO")
    print(f"Total de arquivos processados: {total_processed}")
    print(f"Total de arquivos atualizados: {total_updated}")
    print("=" * 60)


if __name__ == "__main__":
    main()

