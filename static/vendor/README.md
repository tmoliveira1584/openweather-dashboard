# Bibliotecas de terceiros

Cópias locais servidas pelo próprio backend, sem CDN em tempo de execução (guardrail 2 de `docs/arquitetura.md`). Não edite estes arquivos: para atualizar, baixe a nova versão, confira a integridade e registre aqui os novos hashes.

## Leaflet 1.9.4

| Item | Valor |
|---|---|
| Versão | 1.9.4 |
| Licença | BSD-2-Clause (`leaflet-1.9.4/LICENSE`) |
| Origem | `https://registry.npmjs.org/leaflet/-/leaflet-1.9.4.tgz` (pasta `dist/` e `LICENSE` do pacote) |
| Integridade do pacote | `sha512-nxS1ynzJOmOlHp+iL3FyWqK89GtNL8U8rvlMOsQdTTssxZwCXh8N2NB3GDQOL+YR3XnWyZAxwQixURb+FA74PA==`, igual ao `dist.integrity` do registro do npm |
| Conferência independente | SHA-256 do `leaflet.js` e do `leaflet.css` iguais aos valores de integridade (SRI) publicados em `https://leafletjs.com/download.html` |
| Data da cópia | 2026-10-05 |

Arquivos copiados e SHA-256:

| Arquivo | SHA-256 |
|---|---|
| `leaflet-1.9.4/leaflet.js` | `db49d009c841f5ca34a888c96511ae936fd9f5533e90d8b2c4d57596f4e5641a` |
| `leaflet-1.9.4/leaflet.css` | `a7837102824184820dfa198d1ebcd109ff6d0ff9a2672a074b9a1b4d147d04c6` |
| `leaflet-1.9.4/LICENSE` | `53e8dc25862014e4324741ca18fbe3611e11d42ef69f59f86ea8c5389647d4cb` |
| `leaflet-1.9.4/images/layers.png` | `1dbbe9d028e292f36fcba8f8b3a28d5e8932754fc2215b9ac69e4cdecf5107c6` |
| `leaflet-1.9.4/images/layers-2x.png` | `066daca850d8ffbef007af00b06eac0015728dee279c51f3cb6c716df7c42edf` |
| `leaflet-1.9.4/images/marker-icon.png` | `574c3a5cca85f4114085b6841596d62f00d7c892c7b03f28cbfa301deb1dc437` |
| `leaflet-1.9.4/images/marker-icon-2x.png` | `00179c4c1ee830d3a108412ae0d294f55776cfeb085c60129a39aa6fc4ae2528` |
| `leaflet-1.9.4/images/marker-shadow.png` | `264f5c640339f042dd729062cfc04c17f8ea0f29882b538e3848ed8f10edb4da` |

Conferir (Git Bash, nesta pasta):

```bash
sha256sum leaflet-1.9.4/leaflet.js leaflet-1.9.4/leaflet.css leaflet-1.9.4/LICENSE leaflet-1.9.4/images/*.png
```

Os arquivos `leaflet-src.js` e `*.map` do pacote não foram copiados, porque não são usados em execução. Com o DevTools aberto, o Chrome pode registrar um 404 do `leaflet.js.map`, sem efeito na página.

O `.gitattributes` da raiz desliga a conversão de fim de linha nesta pasta, para que os hashes acima continuem conferindo depois do checkout.
