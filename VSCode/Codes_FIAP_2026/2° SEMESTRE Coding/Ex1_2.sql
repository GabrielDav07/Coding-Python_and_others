USE seguranca;

CREATE TABLE IF NOT EXISTS alertas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    ip_origem VARCHAR(45) NOT NULL,
    severidade ENUM('baixa', 'media', 'alta', 'critica') NOT NULL,
    status VARCHAR(20) DEFAULT 'aberto',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO alertas (tipo, ip_origem, severidade, status, criado_em) VALUES
('BRUTE_FORCE',  '185.220.101.1', 'critica', 'aberto', NOW()),
('PORT_SCAN',    '45.33.32.156',  'alta',    'aberto', NOW()),
('SQL_INJECTION','91.240.118.172','alta',    'aberto', NOW()),
('XSS_ATTEMPT',  '192.168.1.80',  'media',   'aberto', NOW());

SELECT * FROM alertas 
WHERE severidade = 'alta';

UPDATE alertas 
SET status = 'resolvido' 
WHERE id = 1;

SELECT severidade, COUNT(*) AS total
FROM alertas
GROUP BY severidade
ORDER BY total DESC;

DELETE FROM alertas 
WHERE criado_em < NOW() - INTERVAL 90 DAY;