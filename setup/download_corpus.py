"""
download_corpus.py
Automatically downloads all public regulatory documents for the corpus.
One document (Sabadell Pillar III) requires a manual download — instructions printed at end.
"""

import os
import requests
from pathlib import Path
from tqdm import tqdm

CORPUS_DIR = Path("data/corpus")
CORPUS_DIR.mkdir(parents=True, exist_ok=True)

# ─── Documents that can be auto-downloaded ────────────────────────────────────
AUTO_DOCS = [
    {
        "id": "eba_aml_2021",
        "filename": "EBA_AML_Guidelines_2021.pdf",
        "url": "https://www.eba.europa.eu/sites/default/files/document_library/Publications/Guidelines/2021/EBA-GL-2021-02%20Guidelines%20on%20CDD%20and%20the%20factors%20credit%20and%20financial%20institutions%20should%20consider%20when%20assessing%20the%20ML%20TF%20risk/1001411/EBA%20GL%202021%2002%20Final%20Report%20on%20GL%20on%20CDD%20and%20ML%20TF%20Risk%20Factors.pdf",
        "description": "EBA Guidelines on Anti-Money Laundering (AML/CFT)",
        "fallback_url": "https://www.eba.europa.eu/sites/default/files/document_library/Publications/Guidelines/2021/EBA-GL-2021-02%20Guidelines%20on%20CDD%20and%20the%20factors%20credit%20and%20financial%20institutions%20should%20consider%20when%20the%20ML%20TF%20risk/1001411/EBA%20GL%202021%2002%20Final%20Report%20on%20GL%20on%20CDD%20and%20ML%20TF%20Risk%20Factors.pdf"
    },
    {
        "id": "mifid2_directive",
        "filename": "MiFID2_Directive_2014_65_EU.pdf",
        "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32014L0065",
        "description": "MiFID II Directive (2014/65/EU) — EUR-Lex",
        "fallback_url": None
    },
    {
        "id": "gdpr_regulation",
        "filename": "GDPR_Regulation_2016_679_EU.pdf",
        "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32016R0679",
        "description": "GDPR Regulation (2016/679/EU) — EUR-Lex",
        "fallback_url": None
    },
]

# ─── Documents requiring manual download ──────────────────────────────────────
MANUAL_DOCS = [
    {
        "id": "sabadell_pillar3_2024",
        "filename": "Sabadell_Pillar3_2024.pdf",
        "url": "https://www.grupbancsabadell.com/corp/en/shareholders-and-investors/financial-information/annual-accounts-and-reports.html",
        "description": "Banc Sabadell Pillar III Risk Disclosures 2024",
        "instruction": (
            "1. Go to: https://www.grupbancsabadell.com/corp/en/shareholders-and-investors/"
            "financial-information/annual-accounts-and-reports.html\n"
            "   2. Download the 'Pillar 3 2024' PDF\n"
            "   3. Save it as: data/corpus/Sabadell_Pillar3_2024.pdf"
        )
    },
    {
        "id": "basel3_bis",
        "filename": "Basel3_BIS_Framework.pdf",
        "url": "https://www.bis.org/bcbs/publ/d424.pdf",
        "description": "Basel III Framework — BIS",
        "instruction": (
            "1. Go to: https://www.bis.org/bcbs/publ/d424.pdf\n"
            "   2. Download and save as: data/corpus/Basel3_BIS_Framework.pdf\n"
            "   (Some browsers download it automatically — just rename and move the file)"
        )
    },
]


def download_file(url: str, dest: Path, description: str) -> bool:
    """Download a file with progress bar. Returns True on success."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; academic-research-bot/1.0)"}
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()

        total = int(response.headers.get("content-length", 0))
        with open(dest, "wb") as f, tqdm(
            desc=f"  {description[:50]}",
            total=total,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            leave=False
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                bar.update(len(chunk))

        size_kb = dest.stat().st_size / 1024
        if size_kb < 10:
            dest.unlink()
            return False
        return True

    except Exception as e:
        if dest.exists():
            dest.unlink()
        return False


def main():
    print("\n" + "="*60)
    print("  Corpus Download Script")
    print("  Banc Sabadell RAG Comparison Project")
    print("="*60 + "\n")

    succeeded = []
    failed = []

    # ── Auto downloads ──────────────────────────────────────────
    print("Attempting automatic downloads...\n")
    for doc in AUTO_DOCS:
        dest = CORPUS_DIR / doc["filename"]
        if dest.exists():
            print(f"  ✓ Already exists: {doc['filename']}")
            succeeded.append(doc["filename"])
            continue

        print(f"  Downloading: {doc['description']}")
        ok = download_file(doc["url"], dest, doc["description"])

        if not ok and doc.get("fallback_url"):
            print(f"    Primary URL failed, trying fallback...")
            ok = download_file(doc["fallback_url"], dest, doc["description"])

        if ok:
            size_kb = dest.stat().st_size / 1024
            print(f"  ✓ Saved: {doc['filename']} ({size_kb:.0f} KB)")
            succeeded.append(doc["filename"])
        else:
            print(f"  ✗ Failed: {doc['filename']} — see manual instructions below")
            failed.append(doc)

    # ── Check manual docs ───────────────────────────────────────
    print("\nChecking manually-downloaded documents...\n")
    manual_needed = []
    for doc in MANUAL_DOCS:
        dest = CORPUS_DIR / doc["filename"]
        if dest.exists():
            size_kb = dest.stat().st_size / 1024
            print(f"  ✓ Found: {doc['filename']} ({size_kb:.0f} KB)")
            succeeded.append(doc["filename"])
        else:
            print(f"  ✗ Missing: {doc['filename']}")
            manual_needed.append(doc)

    # ── Create placeholder text files for missing docs ──────────
    # So the pipeline can run even with partial corpus
    _create_fallback_texts()

    # ── Summary ─────────────────────────────────────────────────
    print("\n" + "="*60)
    print(f"  Downloaded: {len(succeeded)} documents")
    print(f"  Missing:    {len(failed) + len(manual_needed)} documents")
    print("="*60)

    if manual_needed or failed:
        print("\n⚠  MANUAL DOWNLOAD REQUIRED for these documents:\n")
        for doc in manual_needed + failed:
            print(f"  [{doc['id']}] {doc['description']}")
            print(f"   {doc.get('instruction', 'Download from: ' + doc['url'])}\n")
    else:
        print("\n✓ All documents downloaded successfully!")

    print("\nCorpus directory:", CORPUS_DIR.resolve())
    print("Total documents:", len(list(CORPUS_DIR.glob("*.pdf"))) + len(list(CORPUS_DIR.glob("*.txt"))))


def _create_fallback_texts():
    """
    Create rich text fallback files for documents that couldn't be downloaded.
    These contain representative regulatory content so the pipeline works immediately.
    """
    fallbacks = {
        "EBA_AML_Guidelines_SAMPLE.txt": """
EBA Guidelines on Anti-Money Laundering and Counter-Terrorist Financing (AML/CFT)
EBA/GL/2021/02 — Final Guidelines

1. SUBJECT MATTER AND SCOPE
These Guidelines apply to credit institutions and financial institutions within the meaning of Directive (EU) 2015/849.

2. CUSTOMER DUE DILIGENCE (CDD)
2.1 Institutions shall apply CDD measures when establishing a business relationship.
2.2 CDD measures include: identifying and verifying customer identity, identifying beneficial owners, and understanding the business relationship.

3. ENHANCED DUE DILIGENCE (EDD)
3.1 Institutions shall apply EDD measures in higher-risk situations including:
    - Business relationships or transactions involving high-risk third countries
    - Correspondent banking relationships
    - Transactions involving Politically Exposed Persons (PEPs)
    - Complex or unusual transactions with no apparent economic purpose

4. POLITICALLY EXPOSED PERSONS (PEPs)
4.1 For PEPs, institutions must obtain senior management approval before establishing business relationships.
4.2 Institutions shall take adequate measures to establish the source of wealth and source of funds of PEPs.
4.3 Enhanced ongoing monitoring of the business relationship shall be conducted for PEPs.

5. BENEFICIAL OWNERSHIP
5.1 Institutions shall identify and verify the identity of beneficial owners, defined as natural persons who own or control more than 25% of shares or voting rights.
5.2 Where no natural person can be identified as beneficial owner, institutions shall identify the senior managing official.

6. SUSPICIOUS ACTIVITY REPORTING (SAR)
6.1 Institutions shall file a suspicious transaction report (STR) with the national Financial Intelligence Unit (FIU) where they suspect money laundering or terrorist financing.
6.2 The filing of a STR must not be disclosed to the customer or third parties (tipping-off prohibition).

7. RISK-BASED APPROACH
7.1 Institutions shall implement a risk-based approach, conducting a firm-wide risk assessment covering customer risk, product and service risk, delivery channel risk, and geographic risk.
7.2 Simplified Due Diligence (SDD) may be applied where the risk of ML/TF is low, subject to regulatory approval.

8. TRANSACTION MONITORING
8.1 Institutions shall monitor transactions to detect unusual or suspicious patterns.
8.2 Transaction monitoring systems shall be calibrated to the institution's risk profile and reviewed regularly.
""",
        "Basel3_BIS_SAMPLE.txt": """
Basel III: A Global Regulatory Framework for More Resilient Banks
Bank for International Settlements (BIS) — BCBS Publication d424

1. OVERVIEW
Basel III strengthens bank capital requirements and introduces new regulatory requirements on bank liquidity and bank leverage. The framework aims to improve the banking sector's ability to absorb shocks arising from financial and economic stress.

2. CAPITAL REQUIREMENTS

2.1 Common Equity Tier 1 (CET1)
- Minimum CET1 ratio: 4.5% of risk-weighted assets (RWA)
- CET1 consists of: common shares, retained earnings, accumulated other comprehensive income
- Instruments must be perpetual and discretionary as to dividends

2.2 Tier 1 Capital
- Minimum Tier 1 capital ratio: 6% of RWA
- Tier 1 = CET1 + Additional Tier 1 (AT1)
- AT1 instruments must be perpetual with no maturity date

2.3 Total Capital
- Minimum Total Capital ratio: 8% of RWA
- Total Capital = Tier 1 + Tier 2 (T2)
- T2 instruments include subordinated debt with minimum 5-year maturity

2.4 Capital Conservation Buffer
- 2.5% CET1 above minimum requirements
- Restricts distributions when buffer is drawn down
- Purpose: build up capital outside periods of stress

2.5 Countercyclical Buffer
- 0–2.5% CET1, set by national authorities
- Activated during periods of excess credit growth
- Purpose: protect banking sector from losses from excessive credit growth

3. RISK-WEIGHTED ASSETS (RWA)

3.1 Credit Risk
- Standardised Approach: risk weights assigned based on external credit ratings
- Internal Ratings-Based (IRB) Approach: banks estimate probability of default (PD), loss given default (LGD), and exposure at default (EAD)
- Retail exposures: 75% risk weight under standardised approach
- Mortgages secured on residential property: 35% risk weight

3.2 Market Risk
- Revised Fundamental Review of the Trading Book (FRTB)
- Standardised Approach and Internal Models Approach (IMA)
- Replaces Value-at-Risk (VaR) with Expected Shortfall (ES) at 97.5% confidence level

3.3 Operational Risk
- Standardised Measurement Approach (SMA)
- Based on Business Indicator Component (BIC) and Internal Loss Multiplier (ILM)

4. LIQUIDITY REQUIREMENTS

4.1 Liquidity Coverage Ratio (LCR)
- Minimum 100% LCR requirement
- LCR = Stock of High Quality Liquid Assets (HQLA) / Total net cash outflows over 30 days
- Ensures banks can survive a significant stress scenario for 30 days

4.2 Net Stable Funding Ratio (NSFR)
- Minimum 100% NSFR requirement
- NSFR = Available Stable Funding (ASF) / Required Stable Funding (RSF)
- Promotes more medium and long-term funding of assets

5. LEVERAGE RATIO
- Minimum Tier 1 leverage ratio: 3%
- Non-risk-based backstop measure
- Calculated as Tier 1 capital divided by total exposure measure
""",
        "MiFID2_SAMPLE.txt": """
MiFID II — Markets in Financial Instruments Directive (2014/65/EU)
Key Articles for Banking and Investment Services

ARTICLE 24 — GENERAL PRINCIPLES AND INFORMATION TO CLIENTS
1. Investment firms shall act honestly, fairly and professionally in accordance with the best interests of clients.
2. All information, including marketing communications, addressed by the firm to clients shall be fair, clear and not misleading.
3. Investment firms shall provide clients with appropriate information about: the firm and its services, financial instruments and proposed investment strategies, execution venues, and all costs and charges.

ARTICLE 25 — ASSESSMENT OF SUITABILITY AND APPROPRIATENESS
1. Investment firms shall obtain necessary information regarding the client's or potential client's knowledge and experience in the investment field, financial situation including ability to bear losses, and investment objectives including risk tolerance.
2. SUITABILITY TEST: For portfolio management and investment advice, firms must ensure the product is suitable for the client considering their financial situation, investment objectives, and knowledge.
3. APPROPRIATENESS TEST: For non-advised services (execution only), firms must assess whether the client has the knowledge and experience to understand the risks.
4. Where firms determine that a product is not suitable or appropriate, they must warn the client.

ARTICLE 27 — BEST EXECUTION
1. Investment firms shall take all sufficient steps to obtain the best possible result for their clients when executing orders, taking into account price, costs, speed, likelihood of execution and settlement, size, nature, and any other consideration relevant to order execution.
2. Firms must establish and implement an order execution policy defining procedures for complying with best execution.
3. Firms must provide annual reports on the top 5 execution venues used per class of financial instrument.

ARTICLE 30 — TRANSACTIONS EXECUTED WITH ELIGIBLE COUNTERPARTIES
1. Investment firms may deal with eligible counterparties without applying Articles 24, 25, and 27.
2. Eligible counterparties include: investment firms, credit institutions, insurance companies, UCITS management companies, pension funds, and national governments.

PRODUCT GOVERNANCE (Articles 16 and 24)
- Manufacturers must identify a target market for each financial instrument
- Distributors must understand financial instruments and have a distribution strategy compatible with the target market
- Products must be reviewed regularly to ensure they remain consistent with the target market
- High-risk products (complex structured products, leveraged instruments) require enhanced disclosure

KEY INVESTOR INFORMATION DOCUMENT (KIID)
- Required for UCITS funds and PRIIPs (Packaged Retail and Insurance-based Investment Products)
- Must be provided to retail clients before purchase
- Standardised format: 2-3 pages, including risk indicator (1–7 scale), performance scenarios, and costs
""",
        "GDPR_Banking_SAMPLE.txt": """
GDPR Application in Banking and Financial Services
Summary of Key Obligations for Credit Institutions

1. LAWFUL BASIS FOR PROCESSING (Article 6)
Banks may process personal data under the following lawful bases:
- Contractual necessity: processing required to perform the contract (e.g., account management, loan processing)
- Legal obligation: processing required by law (e.g., AML reporting, tax reporting, CRD IV compliance)
- Legitimate interests: where bank interests override individual interests, subject to balancing test
- Consent: freely given, specific, informed and unambiguous — rarely the appropriate basis for banking

2. SPECIAL CATEGORIES OF DATA (Article 9)
Banks must exercise heightened caution with: health data (relevant for insurance products), biometric data (facial recognition, fingerprints for authentication), data on criminal convictions (relevant for AML/KYC processes).

3. DATA SUBJECT RIGHTS
3.1 Right of access (Article 15): Customers have the right to obtain confirmation of whether data is processed and a copy of their personal data. Response within 1 month.
3.2 Right to rectification (Article 16): Customers may request correction of inaccurate data. Critical for credit scoring applications.
3.3 Right to erasure (Article 17): The 'right to be forgotten'. Limited in banking — legal retention obligations typically override erasure requests.
3.4 Right to data portability (Article 20): Customers can receive their data in a machine-readable format. Relevant to PSD2 open banking requirements.
3.5 Rights related to automated decision-making (Article 22): Customers have the right not to be subject to solely automated decisions with significant effects. Credit scoring algorithms must include human review capability.

4. DATA BREACH NOTIFICATION (Article 33 & 34)
4.1 Supervisory authority notification: Within 72 hours of becoming aware of a personal data breach, unless the breach is unlikely to result in risk to individuals.
4.2 Notification to affected individuals: Without undue delay when the breach is likely to result in high risk to individuals.
4.3 Banks must maintain a record of all data breaches, regardless of whether they are reported.

5. DATA PROTECTION OFFICER (DPO)
Banks are required to appoint a DPO (Article 37) as they process personal data on a large scale as a core activity.
The DPO must: have expert knowledge of data protection law, operate independently, report to the highest management level, and be accessible to data subjects.

6. DATA MINIMISATION AND RETENTION
6.1 Banks should only collect data that is adequate, relevant, and limited to what is necessary.
6.2 Retention periods for banking data are governed by both GDPR and sector-specific legislation:
    - AML records: 5 years after end of business relationship (AMLD5)
    - Credit files: duration of credit plus relevant statute of limitations
    - Transaction records: minimum 5 years (PSD2), up to 10 years for AML purposes

7. PRIVACY BY DESIGN AND DEFAULT (Article 25)
Banks must implement technical and organisational measures to integrate data protection into processing activities from the outset.
"""
    }

    fallback_dir = CORPUS_DIR / "samples"
    fallback_dir.mkdir(exist_ok=True)

    for filename, content in fallbacks.items():
        path = fallback_dir / filename
        if not path.exists():
            path.write_text(content.strip())

    print(f"\n  ✓ Created {len(fallbacks)} sample regulatory text files in data/corpus/samples/")
    print("    These ensure the pipeline works even before manual PDFs are downloaded.")


if __name__ == "__main__":
    main()
