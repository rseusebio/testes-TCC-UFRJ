# Scripts de Teste de Carga k6

Este projeto contém scripts de teste de carga k6 projetados para testar diferentes cenários para sua aplicação usando os protocolos HTTP e gRPC.

## Cenários de Teste Disponíveis

### Testes HTTP (script.ts)
- **Smoke Test**: Carga mínima para verificar se o sistema funciona (1 minuto, 1 usuário)
- **Teste de Carga Média**: Carga normal esperada (9 minutos, aumenta até 50 usuários)
- **Teste de Alta Carga**: Estressar o sistema sob alta carga (9 minutos, aumenta até 200 usuários)
- **Teste de Pico**: Testar o comportamento do sistema sob picos súbitos de tráfego (3 minutos, picos até 500 usuários)
- **Teste de Breakpoint**: Aumentar gradualmente a carga até o sistema quebrar (18 minutos, aumenta até 1000 usuários)

### Testes gRPC (grpc-script.ts)
- **Smoke Test**: Carga mínima para verificar se o sistema gRPC funciona (1 minuto, 1 usuário)
- **Teste de Carga Média**: Carga normal esperada para gRPC (9 minutos, aumenta até 50 usuários)
- **Teste de Alta Carga**: Estressar o sistema gRPC sob alta carga (9 minutos, aumenta até 200 usuários)
- **Teste de Pico**: Testar o comportamento do sistema gRPC sob picos súbitos de tráfego (3 minutos, picos até 500 usuários)
- **Teste de Breakpoint**: Aumentar gradualmente a carga gRPC até o sistema quebrar (18 minutos, aumenta até 1000 usuários)

## Executando Testes Individuais

### Testes HTTP
```bash
# Executar teste HTTP smoke (recomendado para começar)
npm run test:smoke

# Executar teste HTTP de carga média
npm run test:average_load

# Executar teste HTTP de alta carga
npm run test:high_load

# Executar teste HTTP de pico
npm run test:spike

# Executar teste HTTP de breakpoint
npm run test:breakpoint
```

### Testes gRPC
```bash
# Executar teste gRPC smoke
npm run grpc:smoke

# Executar teste gRPC de carga média
npm run grpc:average_load

# Executar teste gRPC de alta carga
npm run grpc:high_load

# Executar teste gRPC de pico
npm run grpc:spike

# Executar teste gRPC de breakpoint
npm run grpc:breakpoint
```

## Executando Todos os Testes

```bash
# Executar todos os testes HTTP sequencialmente
npm run test:all

# Executar todos os testes gRPC sequencialmente
npm run grpc:all

# Executar ambas as suítes de teste HTTP e gRPC
npm run test:both
```

## Configuração dos Testes

Cada cenário de teste está configurado com:
- **Limites de performance**: 95% das requisições devem ser concluídas em menos de 2 segundos
- **Limite de taxa de erro**: A taxa de erro deve ser menor que 10%
- **Geração dinâmica de payload**: Cada requisição gera dados aleatórios de cliente, produtos e informações de pagamento

## Endpoints de Destino

### Endpoint HTTP
```
http://54.198.53.242:8080/order
```

### Endpoint gRPC
```
54.198.53.242:9090
```

Para alterar os endpoints de destino, modifique a variável `url` em `script.ts` e o endereço de conexão em `grpc-script.ts`.

## Comparação de Protocolos

| Aspecto | HTTP | gRPC |
|---------|------|------|
| Protocolo | HTTP/1.1 | HTTP/2 |
| Serialização | JSON | Protocol Buffers |
| Performance | Boa | Melhor (binário, multiplexação) |
| Suporte a Navegador | Nativo | Limitado (requer gRPC-Web) |
| Streaming | Limitado | Suporte completo |
| Geração de Código | Manual | Automática a partir de .proto |

## Pré-requisitos

Certifique-se de ter o k6 instalado em seu sistema:

```bash
# macOS
brew install k6

# Windows
choco install k6

# Linux
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

## Entendendo os Resultados

O k6 exibirá métricas detalhadas incluindo:

### Métricas HTTP
- `http_req_duration`: Percentis de duração das requisições
- `http_req_rate`: Taxa de requisições
- `http_req_failed`: Taxa de erros
- `http_reqs`: Total de requisições

### Métricas gRPC
- `grpc_req_duration`: Percentis de duração das requisições
- `grpc_req_rate`: Taxa de requisições
- `grpc_req_failed`: Taxa de erros
- `grpc_reqs`: Total de requisições

### Métricas Comuns
- `vus`: Contagem de usuários virtuais
- `data_received`: Taxas de transferência de dados
- `data_sent`: Taxas de dados enviados

Procure por verificações falhadas ou violações de limites para identificar problemas de performance.

## Estrutura de Arquivos

```
final-project-tests/
├── script.ts          # Script de teste de carga HTTP
├── grpc-script.ts     # Script de teste de carga gRPC
├── order.proto        # Definição de protocol buffer
├── package.json       # Scripts NPM e dependências
└── README.md          # Esta documentação
```

## Solução de Problemas

### Problemas de Conexão gRPC
- Certifique-se de que o servidor gRPC está rodando na porta especificada (9090)
- Verifique se o servidor suporta conexões inseguras (plaintext)
- Verifique se o arquivo .proto corresponde à definição de serviço do servidor

### Problemas de Conexão HTTP
- Certifique-se de que o servidor HTTP está rodando na porta especificada (8080)
- Verifique se o endpoint aceita requisições POST com payloads JSON
- Verifique se o formato da resposta corresponde à estrutura esperada

## Cenários de Teste

### 1. Smoke Test
- **Propósito**: Verificar se o sistema funciona sob carga mínima
- **Configuração**: 1 usuário virtual por 1 minuto
- **Caso de Uso**: Validação rápida de que a API está respondendo corretamente

### 2. Teste de Carga Média
- **Propósito**: Testar carga normal esperada
- **Configuração**: Aumenta de 10 para 50 usuários em 2 minutos, mantém 50 usuários por 5 minutos, depois diminui
- **Caso de Uso**: Simular carga típica de produção

### 3. Teste de Alta Carga
- **Propósito**: Teste de estresse do sistema
- **Configuração**: Aumenta de 50 para 200 usuários em 2 minutos, mantém 200 usuários por 5 minutos, depois diminui
- **Caso de Uso**: Testar performance do sistema sob alto estresse

### 4. Teste de Pico
- **Propósito**: Testar o comportamento do sistema durante picos súbitos de tráfego
- **Configuração**: Linha de base de 10 usuários, picos até 500 usuários por 1 minuto, depois retorna à linha de base
- **Caso de Uso**: Simular picos de tráfego (ex.: promoções relâmpago, conteúdo viral)

### 5. Teste de Breakpoint
- **Propósito**: Encontrar o ponto de quebra do sistema aumentando gradualmente a carga
- **Configuração**: Aumenta gradualmente de 1 para 1000 usuários em estágios de 2 minutos (10, 25, 50, 100, 200, 400, 600, 800, 1000)
- **Caso de Uso**: Determinar capacidade máxima e identificar padrões de degradação de performance
- **O que Observar**: 
  - Degradação do tempo de resposta
  - Aumento da taxa de erros
  - Esgotamento de recursos do sistema
  - Ponto onde os limites de performance são excedidos

## Limites de Performance

O script inclui limites de performance:
- 95% das requisições devem ser concluídas em 2 segundos
- A taxa de erro deve ser menor que 10%

## Executando os Testes

### Pré-requisitos
1. Instale o k6: https://k6.io/docs/getting-started/installation/
2. Certifique-se de que seu endpoint da API está rodando em `http://34.201.38.94:8080/order`

### Executar Todos os Cenários
```bash
k6 run script.ts
```

### Executar Cenários Específicos
Você pode executar cenários individuais modificando o script ou usando o filtro de cenários do k6:

```bash
# Executar apenas teste smoke
k6 run --env TEST_TYPE=smoke script.ts

# Executar apenas teste de carga média
k6 run --env TEST_TYPE=average_load script.ts

# Executar apenas teste de alta carga
k6 run --env TEST_TYPE=high_load script.ts

# Executar apenas teste de pico
k6 run --env TEST_TYPE=spike script.ts

# Executar apenas teste de breakpoint
k6 run --env TEST_TYPE=breakpoint script.ts
```

### Personalizar Parâmetros dos Testes
Você pode modificar os seguintes parâmetros no script:
- `vus`: Número de usuários virtuais
- `duration`: Duração do teste
- `stages`: Padrões de aumento/diminuição
- `thresholds`: Critérios de performance

## Resultados Esperados

O script gerará:
- Métricas em tempo real durante a execução do teste
- Relatório resumido com status de aprovação/falha para cada limite
- Métricas detalhadas para cada cenário de teste

## Monitoramento

Observe:
- Tempos de resposta excedendo os limites
- Altas taxas de erro
- Uso de recursos do sistema
- Disponibilidade do endpoint da API

### Análise do Teste de Breakpoint
Ao executar o teste de breakpoint, preste atenção especial a:
1. **Curva de Tempo de Resposta**: Procure o ponto onde os tempos de resposta começam a aumentar exponencialmente
2. **Pico de Taxa de Erro**: Identifique quando os erros começam a ocorrer frequentemente
3. **Platô de Throughput**: Observe quando a taxa de requisições para de aumentar apesar de mais usuários
4. **Gargalos de Recursos**: Monitore o uso de CPU, memória e rede

## Solução de Problemas

1. **Erros de conexão**: Verifique se a URL do endpoint da API está correta e acessível
2. **Altas taxas de erro**: Verifique se a API consegue lidar com a carga
3. **Erros de timeout**: Considere aumentar os limites de tempo de resposta ou reduzir a carga
4. **Problemas de memória**: Reduza o número de usuários virtuais se seu sistema não conseguir lidar com a carga 