import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
METADATA_PATH = DATA_DIR / "synthetic" / "metadata.json"
GROUND_TRUTH_PATH = DATA_DIR / "eval" / "ground_truth_shipments.json"
GOLD_SET_PATH = DATA_DIR / "eval" / "gold_set.json"

def build_gold_set():
    # 1. Load source files
    if not METADATA_PATH.exists():
        raise FileNotFoundError(f"Metadata file not found: {METADATA_PATH}")
    if not GROUND_TRUTH_PATH.exists():
        raise FileNotFoundError(f"Ground truth file not found: {GROUND_TRUTH_PATH}")

    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    valid_doc_ids = {m["doc_id"] for m in metadata}

    with open(GROUND_TRUTH_PATH, "r", encoding="utf-8") as f:
        ground_truth = json.load(f)

    # 2. Define the 30 evaluation questions
    gold_questions = [
        # --- 1. exact_id_lookup (6 questions: 3 English, 3 Roman Urdu) ---
        {
            "q_id": "Q-01",
            "category": "exact_id_lookup",
            "question": "Which container is assigned to Purchase Order PO-9841?",
            "user_tenant_id": "exp_a",
            "expected_status": "SUPPORTED",
            "expected_doc_ids": ["DOC-SHP01-PO", "DOC-SHP01-BL"],
            "expected_answer_keywords": ["C-402", "PO-9841", "container"],
            "expected_citation_strings": [
                "Container No.: C-402",
                "PO-9841 / C-402 / 1-500",
                "loading on container C-402"
            ]
        },
        {
            "q_id": "Q-02",
            "category": "exact_id_lookup",
            "question": "Purchase Order PO-9842 ka container number kya hai aur yeh kis vessel par load hua hai?",
            "user_tenant_id": "exp_b",
            "expected_status": "SUPPORTED",
            "expected_doc_ids": ["DOC-SHP02-BL"],
            "expected_answer_keywords": ["C-403", "MV Arabian Wave", "PO-9842"],
            "expected_citation_strings": [
                "Container No.: C-403",
                "Ocean Vessel: MV Arabian Wave",
                "PO-9842 / C-403"
            ]
        },
        {
            "q_id": "Q-03",
            "category": "exact_id_lookup",
            "question": "What is the Letter of Credit number and issuing bank for container C-404?",
            "user_tenant_id": "exp_c",
            "expected_status": "SUPPORTED",
            "expected_doc_ids": ["DOC-SHP03-LC", "DOC-SHP03-GD"],
            "expected_answer_keywords": ["LC-2293", "Bavaria Commercial Kreditbank", "C-404"],
            "expected_citation_strings": [
                "Documentary Credit Number (20): LC-2293",
                "Bavaria Commercial Kreditbank AG, Munich",
                "Linked LC / Financial Doc: LC-2293"
            ]
        },
        {
            "q_id": "Q-04",
            "category": "exact_id_lookup",
            "question": "WeBOC Goods Declaration GD-5516 ke sath konsa Purchase Order aur container linked hai?",
            "user_tenant_id": "exp_a",
            "expected_status": "SUPPORTED",
            "expected_doc_ids": ["DOC-SHP07-GD"],
            "expected_answer_keywords": ["PO-9847", "C-408", "GD-5516"],
            "expected_citation_strings": [
                "GD Number: GD-5516",
                "Linked PO: PO-9847",
                "Container ID: C-408"
            ]
        },
        {
            "q_id": "Q-05",
            "category": "exact_id_lookup",
            "question": "What is the WeBOC Goods Declaration number associated with Letter of Credit LC-2298?",
            "user_tenant_id": "exp_b",
            "expected_status": "SUPPORTED",
            "expected_doc_ids": ["DOC-SHP08-GD"],
            "expected_answer_keywords": ["GD-5517", "LC-2298", "PO-9848"],
            "expected_citation_strings": [
                "GD Number: GD-5517",
                "Linked LC / Financial Doc: LC-2298",
                "Linked PO: PO-9848"
            ]
        },
        {
            "q_id": "Q-06",
            "category": "exact_id_lookup",
            "question": "Purchase Order PO-9849 ke tehat shipment kis port se load hui aur Bill of Lading date kya hai?",
            "user_tenant_id": "exp_c",
            "expected_status": "SUPPORTED",
            "expected_doc_ids": ["DOC-SHP09-BL"],
            "expected_answer_keywords": ["Port Qasim", "2026-04-30", "PO-9849"],
            "expected_citation_strings": [
                "Port of Loading: Port Qasim, Pakistan",
                "Shipped on Board Date: 2026-04-30"
            ]
        },

        # --- 2. multi_hop_root_cause (6 questions: 3 English, 3 Roman Urdu) ---
        {
            "q_id": "Q-07",
            "category": "multi_hop_root_cause",
            "question": "Shipment SHP-01 has received a Customs Hold Notice under GD-5510 and PO-9841. What is the root cause of this hold based on the linked export documents?",
            "user_tenant_id": "exp_a",
            "expected_status": "CONFLICTING_EVIDENCE",
            "expected_doc_ids": [
                "DOC-SHP01-PO",
                "DOC-SHP01-BL",
                "DOC-SHP01-LC",
                "DOC-SHP01-GD",
                "DOC-SHP01-CHN"
            ],
            "expected_answer_keywords": [
                "declared value",
                "LC amount",
                "48,500",
                "45,000",
                "higher",
                "value mismatch"
            ],
            "expected_citation_strings": [
                "Credit Amount (32B): USD 45,000.00",
                "Declared FOB Value: USD 48,500.00",
                "Purchase Order Mentioned: PO-9841",
                "Goods Declaration Mentioned: GD-5510"
            ]
        },
        {
            "q_id": "Q-08",
            "category": "multi_hop_root_cause",
            "question": "Customs Hold Notice ke mutabiq PO-9842 aur GD-5511 ki shipment hold par hai. Tamam linked documents check karke batayein ke hold ki asal waja (root cause) kya hai?",
            "user_tenant_id": "exp_b",
            "expected_status": "CONFLICTING_EVIDENCE",
            "expected_doc_ids": [
                "DOC-SHP02-PO",
                "DOC-SHP02-BL",
                "DOC-SHP02-LC",
                "DOC-SHP02-GD",
                "DOC-SHP02-CHN"
            ],
            "expected_answer_keywords": [
                "HS code",
                "6109.10",
                "6302.60",
                "mismatch",
                "PO",
                "GD",
                "terry towels"
            ],
            "expected_citation_strings": [
                "HS Code: 6109.10",
                "Declared HS Code: 6302.60",
                "Goods Declaration Mentioned: GD-5511"
            ]
        },
        {
            "q_id": "Q-09",
            "category": "multi_hop_root_cause",
            "question": "Consignment SHP-03 is detained under Customs Notice CHN-5512-REV. Tracing from container C-404 and PO-9843 through to LC-2293, what root cause explains the documentary discrepancy?",
            "user_tenant_id": "exp_c",
            "expected_status": "CONFLICTING_EVIDENCE",
            "expected_doc_ids": [
                "DOC-SHP03-PO",
                "DOC-SHP03-BL",
                "DOC-SHP03-LC",
                "DOC-SHP03-GD",
                "DOC-SHP03-CHN"
            ],
            "expected_answer_keywords": [
                "LC expiry date",
                "Bill of Lading date",
                "expired",
                "2026-04-10",
                "2026-04-15",
                "before"
            ],
            "expected_citation_strings": [
                "Date and Place of Expiry (31D): 2026-04-10",
                "Shipped on Board Date: 2026-04-15"
            ]
        },
        {
            "q_id": "Q-10",
            "category": "multi_hop_root_cause",
            "question": "Container C-405 ki shipment GD-5513 par customs ne hold lagaya hai. Letter of Credit LC-2294 aur baqi documents link karke batayein ke konsi documentary requirement poori nahi hui?",
            "user_tenant_id": "exp_a",
            "expected_status": "CONFLICTING_EVIDENCE",
            "expected_doc_ids": [
                "DOC-SHP04-PO",
                "DOC-SHP04-BL",
                "DOC-SHP04-LC",
                "DOC-SHP04-GD",
                "DOC-SHP04-CHN"
            ],
            "expected_answer_keywords": [
                "inspection certificate",
                "Pre-Shipment Inspection",
                "missing",
                "surveyor",
                "LC requirement"
            ],
            "expected_citation_strings": [
                "Pre-Shipment Inspection Certificate issued by an authorized independent surveyor",
                "DOCUMENTS REQUIRED (FIELD 46A)"
            ]
        },
        {
            "q_id": "Q-11",
            "category": "multi_hop_root_cause",
            "question": "Why was shipment SHP-05 placed on administrative hold at Port Qasim after linking WeBOC GD-5514, container C-406, and Bill of Lading?",
            "user_tenant_id": "exp_b",
            "expected_status": "CONFLICTING_EVIDENCE",
            "expected_doc_ids": [
                "DOC-SHP05-PO",
                "DOC-SHP05-BL",
                "DOC-SHP05-LC",
                "DOC-SHP05-GD",
                "DOC-SHP05-CHN"
            ],
            "expected_answer_keywords": [
                "gross weight",
                "weight mismatch",
                "19,850",
                "16,400",
                "BL",
                "GD",
                "differs"
            ],
            "expected_citation_strings": [
                "Gross Weight: 19,850 KG",
                "Gross Weight: 16,400 KG"
            ]
        },
        {
            "q_id": "Q-12",
            "category": "multi_hop_root_cause",
            "question": "Customs Hold Notice CHN-5510-REV mein hold ki waja wazeh nahi hai. PO-9841 se shuru karke LC-2291 aur GD-5510 tak cross-check karein aur batayein ke documents review mein kis value ka discrepancy nikla?",
            "user_tenant_id": "exp_a",
            "expected_status": "CONFLICTING_EVIDENCE",
            "expected_doc_ids": [
                "DOC-SHP01-PO",
                "DOC-SHP01-LC",
                "DOC-SHP01-GD",
                "DOC-SHP01-CHN"
            ],
            "expected_answer_keywords": [
                "GD declared value",
                "48,500",
                "LC amount",
                "45,000",
                "higher",
                "farq",
                "mismatch"
            ],
            "expected_citation_strings": [
                "Declared FOB Value: USD 48,500.00",
                "Credit Amount (32B): USD 45,000.00",
                "Total PO Value: USD 45,000.00"
            ]
        },

        # --- 3. discrepancy_detection (6 questions: 3 English, 3 Roman Urdu) ---
        {
            "q_id": "Q-13",
            "category": "discrepancy_detection",
            "question": "Is there a financial valuation discrepancy between WeBOC GD-5510 and Letter of Credit LC-2291 for shipment SHP-01?",
            "user_tenant_id": "exp_a",
            "expected_status": "CONFLICTING_EVIDENCE",
            "expected_doc_ids": ["DOC-SHP01-LC", "DOC-SHP01-GD"],
            "expected_answer_keywords": [
                "discrepancy",
                "higher",
                "48,500",
                "45,000",
                "GD declared value",
                "LC amount"
            ],
            "expected_citation_strings": [
                "Credit Amount (32B): USD 45,000.00",
                "Declared FOB Value: USD 48,500.00"
            ]
        },
        {
            "q_id": "Q-14",
            "category": "discrepancy_detection",
            "question": "Shipment SHP-02 mein Purchase Order PO-9842 aur Goods Declaration GD-5511 ke darmian HS code ka kya ikhtilaf (discrepancy) hai?",
            "user_tenant_id": "exp_b",
            "expected_status": "CONFLICTING_EVIDENCE",
            "expected_doc_ids": ["DOC-SHP02-PO", "DOC-SHP02-GD"],
            "expected_answer_keywords": [
                "HS code",
                "6109.10",
                "6302.60",
                "PO",
                "GD",
                "ikhtilaf",
                "differs"
            ],
            "expected_citation_strings": [
                "6109.10",
                "Declared HS Code: 6302.60"
            ]
        },
        {
            "q_id": "Q-15",
            "category": "discrepancy_detection",
            "question": "Does the Bill of Lading shipment date for container C-404 comply with the expiry date specified in Letter of Credit LC-2293?",
            "user_tenant_id": "exp_c",
            "expected_status": "CONFLICTING_EVIDENCE",
            "expected_doc_ids": ["DOC-SHP03-BL", "DOC-SHP03-LC"],
            "expected_answer_keywords": [
                "LC expiry date",
                "before",
                "Bill of Lading date",
                "2026-04-10",
                "2026-04-15",
                "expired"
            ],
            "expected_citation_strings": [
                "Date and Place of Expiry (31D): 2026-04-10",
                "Shipped on Board Date: 2026-04-15"
            ]
        },
        {
            "q_id": "Q-16",
            "category": "discrepancy_detection",
            "question": "Letter of Credit LC-2294 ke document checklist ke mutabiq konsa zaroori certificate shipment documents mein mojood nahi hai?",
            "user_tenant_id": "exp_a",
            "expected_status": "CONFLICTING_EVIDENCE",
            "expected_doc_ids": ["DOC-SHP04-LC"],
            "expected_answer_keywords": [
                "Pre-Shipment Inspection Certificate",
                "inspection certificate",
                "missing",
                "surveyor"
            ],
            "expected_citation_strings": [
                "Pre-Shipment Inspection Certificate issued by an authorized independent surveyor",
                "DOCUMENTS REQUIRED (FIELD 46A)"
            ]
        },
        {
            "q_id": "Q-17",
            "category": "discrepancy_detection",
            "question": "Compare the gross weight declared on Bill of Lading with WeBOC Goods Declaration GD-5514 for container C-406. Is there a discrepancy?",
            "user_tenant_id": "exp_b",
            "expected_status": "CONFLICTING_EVIDENCE",
            "expected_doc_ids": ["DOC-SHP05-BL", "DOC-SHP05-GD"],
            "expected_answer_keywords": [
                "gross weight",
                "discrepancy",
                "19,850",
                "16,400",
                "differs",
                "weight mismatch"
            ],
            "expected_citation_strings": [
                "Gross Weight: 19,850 KG",
                "Gross Weight: 16,400 KG"
            ]
        },
        {
            "q_id": "Q-18",
            "category": "discrepancy_detection",
            "question": "Kya Purchase Order PO-9841 ki total value aur Goods Declaration GD-5510 ki declared FOB value aapas mein match karti hain ya koi farq hai?",
            "user_tenant_id": "exp_a",
            "expected_status": "CONFLICTING_EVIDENCE",
            "expected_doc_ids": ["DOC-SHP01-PO", "DOC-SHP01-GD"],
            "expected_answer_keywords": [
                "PO value 45,000",
                "GD value 48,500",
                "farq",
                "mismatch",
                "higher"
            ],
            "expected_citation_strings": [
                "Total PO Value: USD 45,000.00",
                "Declared FOB Value: USD 48,500.00"
            ]
        },

        # --- 4. clean_shipment (4 questions: 2 English, 2 Roman Urdu) ---
        {
            "q_id": "Q-19",
            "category": "clean_shipment",
            "question": "Are there any document discrepancies or compliance conflicts across the PO, BL, LC, and GD for shipment SHP-06?",
            "user_tenant_id": "exp_c",
            "expected_status": "SUPPORTED",
            "expected_doc_ids": [
                "DOC-SHP06-PO",
                "DOC-SHP06-BL",
                "DOC-SHP06-LC",
                "DOC-SHP06-GD"
            ],
            "expected_answer_keywords": [
                "clean",
                "consistent",
                "no discrepancy",
                "matches",
                "64,000",
                "6203.42",
                "9,800"
            ],
            "expected_citation_strings": [
                "Total PO Value: USD 64,000.00",
                "Credit Amount (32B): USD 64,000.00",
                "Declared FOB Value: USD 64,000.00",
                "Gross Weight: 9,800 KG"
            ]
        },
        {
            "q_id": "Q-20",
            "category": "clean_shipment",
            "question": "Shipment SHP-07 ke tamam documents (PO-9847, BL, LC-2297, GD-5516) ki verification ke baad kya koi discrepancy ya farq paya gaya?",
            "user_tenant_id": "exp_a",
            "expected_status": "SUPPORTED",
            "expected_doc_ids": [
                "DOC-SHP07-PO",
                "DOC-SHP07-BL",
                "DOC-SHP07-LC",
                "DOC-SHP07-GD"
            ],
            "expected_answer_keywords": [
                "koi discrepancy nahi",
                "consistent",
                "45,000",
                "6109.10",
                "14,200 KG",
                "fully match"
            ],
            "expected_citation_strings": [
                "Total PO Value: USD 45,000.00",
                "Credit Amount (32B): USD 45,000.00",
                "Declared FOB Value: USD 45,000.00",
                "Gross Weight: 14,200 KG"
            ]
        },
        {
            "q_id": "Q-21",
            "category": "clean_shipment",
            "question": "Verify the consistency of weight, value, and HS code between Bill of Lading and Goods Declaration GD-5517 for shipment SHP-08.",
            "user_tenant_id": "exp_b",
            "expected_status": "SUPPORTED",
            "expected_doc_ids": ["DOC-SHP08-BL", "DOC-SHP08-GD"],
            "expected_answer_keywords": [
                "consistent",
                "no discrepancy",
                "matches",
                "12,500 KG",
                "52,000",
                "6302.60"
            ],
            "expected_citation_strings": [
                "Gross Weight: 12,500 KG",
                "Declared FOB Value: USD 52,000.00",
                "Declared HS Code: 6302.60"
            ]
        },
        {
            "q_id": "Q-22",
            "category": "clean_shipment",
            "question": "Purchase Order PO-9850 aur WeBOC GD-5519 (SHP-10) ke darmian value, quantity aur HS code ka mawazna karein, kya yeh clean shipment hai?",
            "user_tenant_id": "exp_a",
            "expected_status": "SUPPORTED",
            "expected_doc_ids": ["DOC-SHP10-PO", "DOC-SHP10-GD"],
            "expected_answer_keywords": [
                "clean shipment",
                "koi discrepancy nahi",
                "45,000",
                "15,000 PCS",
                "6109.10",
                "match"
            ],
            "expected_citation_strings": [
                "Total PO Value: USD 45,000.00",
                "Declared FOB Value: USD 45,000.00",
                "15,000 PCS",
                "6109.10"
            ]
        },

        # --- 5. insufficient_evidence (4 questions: 2 English, 2 Roman Urdu) ---
        {
            "q_id": "Q-23",
            "category": "insufficient_evidence",
            "question": "What is the declared FOB value and container number for Purchase Order PO-9999?",
            "user_tenant_id": "exp_a",
            "expected_status": "INSUFFICIENT_EVIDENCE",
            "expected_doc_ids": [],
            "expected_answer_keywords": [
                "PO-9999",
                "not found",
                "no evidence",
                "does not exist",
                "insufficient evidence"
            ],
            "expected_citation_strings": []
        },
        {
            "q_id": "Q-24",
            "category": "insufficient_evidence",
            "question": "WeBOC Goods Declaration GD-8888 kis exporter ki hai aur iska shipment status kya hai?",
            "user_tenant_id": "exp_b",
            "expected_status": "INSUFFICIENT_EVIDENCE",
            "expected_doc_ids": [],
            "expected_answer_keywords": [
                "GD-8888",
                "mojood nahi",
                "records mein nahi",
                "insufficient evidence",
                "not found"
            ],
            "expected_citation_strings": []
        },
        {
            "q_id": "Q-25",
            "category": "insufficient_evidence",
            "question": "Which vessel and container were assigned to export consignment under Letter of Credit LC-7777?",
            "user_tenant_id": "exp_c",
            "expected_status": "INSUFFICIENT_EVIDENCE",
            "expected_doc_ids": [],
            "expected_answer_keywords": [
                "LC-7777",
                "not found",
                "no records",
                "insufficient information"
            ],
            "expected_citation_strings": []
        },
        {
            "q_id": "Q-26",
            "category": "insufficient_evidence",
            "question": "Container C-999 ka shipping line, gross weight aur port of discharge kya hai?",
            "user_tenant_id": "exp_a",
            "expected_status": "INSUFFICIENT_EVIDENCE",
            "expected_doc_ids": [],
            "expected_answer_keywords": [
                "C-999",
                "container nahi mila",
                "not found",
                "insufficient evidence"
            ],
            "expected_citation_strings": []
        },

        # --- 6. rbac (4 questions: 2 English, 2 Roman Urdu) ---
        {
            "q_id": "Q-27",
            "category": "rbac",
            "question": "As tenant exp_b, retrieve the Letter of Credit details and declared value for Purchase Order PO-9841.",
            "user_tenant_id": "exp_b",  # SHP-01 belongs to exp_a
            "expected_status": "INSUFFICIENT_EVIDENCE",
            "expected_doc_ids": [],
            "expected_answer_keywords": [
                "access denied",
                "unauthorized",
                "no documents returned",
                "tenant isolation",
                "exp_b",
                "PO-9841"
            ],
            "expected_citation_strings": []
        },
        {
            "q_id": "Q-28",
            "category": "rbac",
            "question": "Main tenant exp_c ka user hoon, mujhe PO-9842 aur GD-5511 ke tamam shipment documents dikhayein.",
            "user_tenant_id": "exp_c",  # SHP-02 belongs to exp_b
            "expected_status": "INSUFFICIENT_EVIDENCE",
            "expected_doc_ids": [],
            "expected_answer_keywords": [
                "access denied",
                "ijazat nahi",
                "no documents",
                "unauthorized",
                "exp_c"
            ],
            "expected_citation_strings": []
        },
        {
            "q_id": "Q-29",
            "category": "rbac",
            "question": "I am logged in under tenant exp_a. Show me the Bill of Lading and customs review notice for container C-404.",
            "user_tenant_id": "exp_a",  # SHP-03 belongs to exp_c
            "expected_status": "INSUFFICIENT_EVIDENCE",
            "expected_doc_ids": [],
            "expected_answer_keywords": [
                "access restricted",
                "no documents returned",
                "unauthorized",
                "exp_a",
                "C-404"
            ],
            "expected_citation_strings": []
        },
        {
            "q_id": "Q-30",
            "category": "rbac",
            "question": "Tenant exp_a ke account se container C-406 aur Goods Declaration GD-5514 ka gross weight aur inspection status check karein.",
            "user_tenant_id": "exp_a",  # SHP-05 belongs to exp_b
            "expected_status": "INSUFFICIENT_EVIDENCE",
            "expected_doc_ids": [],
            "expected_answer_keywords": [
                "access denied",
                "dastiyab nahi",
                "no documents",
                "unauthorized",
                "exp_a"
            ],
            "expected_citation_strings": []
        }
    ]

    # 3. Validation
    assert len(gold_questions) == 30, f"Expected exactly 30 questions, found {len(gold_questions)}"

    category_counts = Counter(q["category"] for q in gold_questions)
    expected_categories = {
        "exact_id_lookup": 6,
        "multi_hop_root_cause": 6,
        "discrepancy_detection": 6,
        "clean_shipment": 4,
        "insufficient_evidence": 4,
        "rbac": 4
    }

    print("\n--- Validating Categories and Counts ---")
    for cat, count in expected_categories.items():
        actual = category_counts.get(cat, 0)
        assert actual == count, f"Category '{cat}' count mismatch: expected {count}, got {actual}"
        print(f"Category: {cat:25s} Count: {actual}")

    # Validate that every expected_doc_id exists in metadata.json
    print("\n--- Validating expected_doc_ids against metadata.json ---")
    invalid_ids = []
    total_doc_refs = 0
    for q in gold_questions:
        for doc_id in q["expected_doc_ids"]:
            total_doc_refs += 1
            if doc_id not in valid_doc_ids:
                invalid_ids.append((q["q_id"], doc_id))

    if invalid_ids:
        raise ValueError(f"Found invalid expected_doc_ids: {invalid_ids}")
    print(f"All {total_doc_refs} document references across all questions successfully validated against metadata.json!")

    # Validate required keys
    required_keys = {
        "q_id",
        "category",
        "question",
        "user_tenant_id",
        "expected_status",
        "expected_doc_ids",
        "expected_answer_keywords",
        "expected_citation_strings"
    }
    allowed_statuses = {"SUPPORTED", "PARTIALLY_SUPPORTED", "CONFLICTING_EVIDENCE", "INSUFFICIENT_EVIDENCE"}

    for q in gold_questions:
        missing_keys = required_keys - set(q.keys())
        assert not missing_keys, f"Question {q['q_id']} missing keys: {missing_keys}"
        assert q["expected_status"] in allowed_statuses, f"Invalid status: {q['expected_status']}"
        assert isinstance(q["expected_doc_ids"], list), "expected_doc_ids must be a list"
        assert isinstance(q["expected_answer_keywords"], list), "expected_answer_keywords must be a list"
        assert isinstance(q["expected_citation_strings"], list), "expected_citation_strings must be a list"

    # 4. Save to data/eval/gold_set.json
    with open(GOLD_SET_PATH, "w", encoding="utf-8") as f:
        json.dump(gold_questions, f, indent=2, ensure_ascii=False)

    print(f"\nSuccessfully wrote {len(gold_questions)} gold evaluation questions to: {GOLD_SET_PATH}\n")

if __name__ == "__main__":
    build_gold_set()
