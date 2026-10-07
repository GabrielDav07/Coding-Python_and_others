CREATE DATABASE IF NOT EXISTS seguranca;
USE seguranca;

CREATE TABLE IF NOT EXISTS ativos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    ip VARCHAR(45) NOT NULL UNIQUE,
    tipo VARCHAR(50) NOT NULL,
    criticidade ENUM('baixa', 'media', 'alta', 'critica') DEFAULT 'media',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vulnerabilidades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cve_id VARCHAR(30) NOT NULL UNIQUE,
    descricao TEXT,
    severidade ENUM('baixa', 'media', 'alta', 'critica') NOT NULL,
    cvss DECIMAL(3, 1) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ativo_vulnerabilidade (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ativo_id INT NOT NULL,
    vuln_id INT NOT NULL,
    status ENUM('aberto', 'em_analise', 'corrigido') DEFAULT 'aberto',
    detectada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ativo FOREIGN KEY (ativo_id) REFERENCES ativos(id) ON DELETE CASCADE,
    CONSTRAINT fk_vuln FOREIGN KEY (vuln_id) REFERENCES vulnerabilidades(id) ON DELETE CASCADE
);

INSERT INTO ativos (nome, ip, tipo, criticidade) 
VALUES ('SRV-WEB01', '192.168.1.10', 'servidor', 'alta');

INSERT INTO vulnerabilidades (cve_id, descricao, severidade, cvss) 
VALUES ('CVE-2024-001', 'SQL Injection no endpoint de login', 'alta', 8.5);

INSERT INTO ativo_vulnerabilidade (ativo_id, vuln_id, status)
VALUES (
    (SELECT id FROM ativos WHERE nome = 'SRV-WEB01'),
    (SELECT id FROM vulnerabilidades WHERE cve_id = 'CVE-2024-001'),
    'aberto'
);

SELECT 
    a.nome AS ativo, 
    a.ip, 
    v.cve_id, 
    v.severidade, 
    v.cvss, 
    av.status 
FROM ativo_vulnerabilidade av
JOIN ativos a ON av.ativo_id = a.id
JOIN vulnerabilidades v ON av.vuln_id = v.id;