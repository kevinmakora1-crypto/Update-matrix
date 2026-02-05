import frappe

def execute():
    """
    Consolidated patch to:
    1. Create Contract Item Category  
    2. Update Contract Items with Item Type, Service Type, Daily Operation, and Category
    
    All data embedded inline - no external files needed
    Fixed: Properly handles merged cells + correct field names
    """
    
    print("\n" + "="*80)
    print("CONTRACT ITEMS CONSOLIDATED PATCH")
    print("="*80 + "\n")
    
    create_contract_item_category()
    update_contract_items()


def create_contract_item_category():
    """Creates the required Contract Item Category if it doesn't exist"""
    
    category_name = "Annual Maintenance of Security & Safety Systems"
    
    if frappe.db.exists("Contract Item Category", category_name):
        print(f"✓ Contract Item Category '{category_name}' already exists\n")
        return
    
    try:
        category_doc = frappe.get_doc({
            "doctype": "Contract Item Category",
            "contract_item_category": category_name
        })
        
        category_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
        print(f"✓ Successfully created Contract Item Category: '{category_name}'\n")
        
    except Exception as e:
        frappe.log_error(f"Error creating Contract Item Category: {str(e)}")
        print(f"✗ Error creating Contract Item Category: {str(e)}")
        frappe.db.rollback()
        raise


def get_contracts_data():
    """Returns the embedded contract items data"""
    
    return {
    "Barbacoa Restaurant-Barbacoa Restaurant-2025-11-09": [
        {
            "item_code": "SER-CLN-000015-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Yusuf Ahmed Alghanim & Sons W.L.L.-Alghanim Industries-2025-11-14": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "M/S Sky Capital Company for Buying and Selling Shares and Bonds Single Person Company-M/S Sky Capital Company-2025-10-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "M/S EZ Outdoor for Land and Marine Trip Supplies W.L.L.-M/S EZ Outdoor for Land and Marine Trip Supplies W.L.L.-2025-09-02": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "One PM Franchising Food Services Company W.L.L.-One PM Franchising Food Services Company W.L.L.-2025-07-17": [
        {
            "item_code": "SER-CLN-000001-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "EMY Restaurant and Snack Company W.L.L-EMY Restaurant and Snack Company W.L.L-2025-07-31": [
        {
            "item_code": "SER-CLN-000001-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Italian Embassy in Kuwait-Italian Embassy in Kuwait-2025-06-25": [
        {
            "item_code": "SER-CWK-000001",
            "item_type": "Items",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": "Annual Maintenance of Security & Safety Systems"
        }
    ],
    "DSV Solutions-DSV A&S-2025-05-18": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "DSV Solutions-DSV Solutions-2025-05-18": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Al-Dhow Engineering General Trading & Contracting Company. LLC-Al Dhow Engineering, Gen. Trd. & Cont . Company-2023-12-31": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "DHLA International Transport Company W.L.L.-DHL JANITORIAL SERVICES-2025-03-01": [
        {
            "item_code": "SER-CLN-000001-NKW-M-26DY-11HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Salhia Real Estate Company-Salhia Real Estate Company-2025-04-15": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "LuLu Center International General Trading and Contracting Co. W.L.L-Lulu Hypermarket - Jaber Mall-2024-11-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "LuLu Center International General Trading and Contracting Co. W.L.L-Lulu Hypermarket Express - Kuwait City-2023-05-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "LuLu Center International General Trading and Contracting Co. W.L.L-Lulu Express - Warehouse Mall-2023-08-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000136-NKW-F-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "LuLu Center International General Trading and Contracting Co. W.L.L-Lulu Fresh Market - Khairan-2023-04-01": [
        {
            "item_code": "SER-CLN-000001-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "LuLu Center International General Trading and Contracting Co. W.L.L-Lulu Hypermarket Egaila-2021-01-26": [
        {
            "item_code": "SER-SEC-000136-NKW-F-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000033-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000391-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "LuLu Center International General Trading and Contracting Co. W.L.L-Lulu Hypermarket Express - Terrace Mall-2021-01-26": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Magic Capitol Company-Magic Capitol Company-2024-11-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-000002-NKW-M-30DY-10HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "NOV Energy Products & Services-NOV Energy Products & Services-2024-11-01": [
        {
            "item_code": "SER-CLN-000083-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "ALMANSOORI PETROLEUM SERVICES LTD-TAQA Well Solutions-2024-12-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-CLN-000083-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "TOTAL FACILITIES COMPANY FOR GENERAL MANAGEMENT-TOTAL FACILITIES COMPANY FOR GENERAL MANAGEMENT-2024-10-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000391-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Altitude roasters-Altitude roasters-2024-05-01": [
        {
            "item_code": "SER-CLN-000015-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Jazeera Airways-Jazeera Airways-2024-12-25": [
        {
            "item_code": "SER-FMG-001710-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-000002-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "AL-Jood Al-Alamiya Al-Tayyiba Company-Al Jood Al Alamiya Al Tayyiba Company-2024-11-01": [
        {
            "item_code": "SER-CLN-000096-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Gulf Consult-Gulf Consult-2024-08-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "WTE O&M Kuwait Sewage Treatment S.P.C.-WTE O&M Kuwait Sewage Treatment S.P.C.-2024-01-30": [
        {
            "item_code": "SER-FMG-000337-KWT-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Siemens IBEE M. Contracting WLL-M/S. Siemens-2024-03-06": [
        {
            "item_code": "SER-FMG-000337-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Austrian Embassy in Kuwait-Austrian Embassy in Kuwait-2024-02-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-22DY-8HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Reem for Hotel & Real Estate Services compay-Reem For Hotel  and  Real estate Services Company-2024-02-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Baker Hughes EHO Ltd-Baker Hughes EHO Ltd-2024-03-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Grand Hyatt Residences-Grand Hyatt Residences-2023-10-02": [
        {
            "item_code": "SER-FMG-000771-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "OCS Express-OCS Express-2023-11-06": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Kuwait National Cinema. K.P.S.C-Warehouse Mall-2023-08-15": [
        {
            "item_code": "SER-FMG-000120-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-000141-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Jashanmal & Co. for General trading-Jashanmal & Co. for General Trading-2023-08-30": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Tamdeen International Restaurants - khiran Mall-Tamdeen International Restaurants - khiran Mall-2023-09-01": [
        {
            "item_code": "SER-FMG-000771-NKW-M-30DY-10HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Kuwaities Distinguished System General Trading Company-Kuwaities Distinguished System General Trading Company-2021-01-10": [
        {
            "item_code": "SER-SEC-000136-NKW-F-30DY-8HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "AlGhanim Industries-Alghanim Industries-2023-06-20": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Al-Baraka Complex-Al-Baraka Complex-2019-05-31": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "The Story Tower-The Story Tower-2017-09-30": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-CLN-000001-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "RCBT-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "European Union-European Union - Kuwait-2023-06-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-22DY-8HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000136-NKW-F-22DY-8HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Grand Hyatt-Grand Hyatt Kuwait-2022-07-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "No",
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000436-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "No",
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000435-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "No",
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000342-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "No",
            "contract_item_category": None
        }
    ],
    "Gulf Express-Gulf Express-2016-12-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Dorrat AlFintas-Durrat Al-Fintas-2018-03-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000391-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-CLN-000001-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Aramex-Aramex-2022-05-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Al-Dhow Engineering General Trading & Contracting Company. LLC-Al-Dhow Engineering General Trading & Contracting Company W.L.L.-2022-05-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Sun and Sand Sports LLC-Sun and Sand Sports LLC-2022-08-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "ZAJIL TELECOM - KEMS-Gulfnet International Company - KEMS-2020-04-16": [
        {
            "item_code": "SER-CLN-000001-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-CLN-000001-NKW-F-26DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Weatherford-Weatherford-2022-04-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-CLN-000001-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "No",
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-000294-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000136-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Tamdeen Shopping Centers Co. K.S.C.C.-360 Car Park-2022-01-01": [
        {
            "item_code": "SER-FMG-000120-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-000141-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Spirit Real Estate Development Co-360 Car Park-2022-01-01": [
        {
            "item_code": "SER-FMG-000120-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-000141-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-000120-NKW-M-30DY-11HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Martyr Asrar Alqabandi bilingual School-Asrar School-2020-01-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Manshar real Estate Co. K.S.C.C-Al Kout Mall Car park-2021-01-01": [
        {
            "item_code": "SER-FMG-000120-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-000141-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Madison and Heig Restaurant Company WLL-Madison & Heig Restaurant Company-2021-03-15": [
        {
            "item_code": "SER-CLN-000001-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "LANDMARK LEISURE KIDS ENTERTAINMENT GAMES CO. W.L.L-Landmark Leisure Kids Entertainment Games Co. W.l.l.-2021-01-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Kuwait Cricket Club-Kuwait Cricket Association-2020-10-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Khaldiya Co. Op-AlKhaldiya CO-OP-2018-09-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-8HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "GCCIA-Gulf Cooperation Council Interconnection Authority (GCCIA)-2021-09-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Engie Services Kuwait-Engie Services-2019-09-14": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-CLN-000001-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-000294-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "DHLA International Transport Company W.L.L.-DHL-2020-01-06": [
        {
            "item_code": "SER-SEC-000136-KWT-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000046-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000033-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000428-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Al-Nasser Tower-Al Nasser Tower-2019-07-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000136-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-CLN-000001-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Aayan Leasing Co.-Aayan Rental & Leasing-2022-06-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Embassy of the kingdom of the Netherlands-Dutch Embassy-2019-03-10": [
        {
            "item_code": "SER-SEC-000136-NKW-M-22DY-8HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Jawad Abdullah AlSaffar Firm For GTC-Jawad AlSaffar-2021-05-10": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Al Arabia Educational Enterprises Co - 1-Arabian Company for Educational Projects KSCC. ( AUM )-2021-09-15": [
        {
            "item_code": "SER-SEC-000136-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Land mark-Landmark Group - Security-2022-07-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000136-NKW-M-8DY-10HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "No",
            "contract_item_category": None
        }
    ],
    "Tamdeen Sports Company K.S.C.C.-Rafa Nadal Tennis Academy-2020-12-01": [
        {
            "item_code": "SER-CLN-000083-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "No",
            "contract_item_category": None
        },
        {
            "item_code": "SER-CLN-000083-NKW-F-26DY-12HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "No",
            "contract_item_category": None
        },
        {
            "item_code": "SER-CLN-000001-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "No",
            "contract_item_category": None
        },
        {
            "item_code": "SER-CLN-000001-NKW-F-26DY-12HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "No",
            "contract_item_category": None
        }
    ],
    "Tamdeen International Restaurants-Tamdeen International Restaurants-2020-08-25": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-CLN-000001-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "M.H. Alshaya Co. W.L.L.-Alshaya Group-2020-04-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-11HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000136-NKW-F-30DY-11HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Al - Futtaim Kuwait for Central Markets Co. W.L.L.-Majed Al-Futtaim-2019-10-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-000294-NKW-M-22DY-8HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Incheon Kuwait Airport Services-T4 Airport-2018-05-26": [
        {
            "item_code": "SER-SEC-000018-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-CLN-000058-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-000263-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000281-KWT-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000028-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-CLN-000083-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-CLN-000096-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-000272-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-CLN-000001-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-000195-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000136-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000055-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-000182-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000023-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-CLN-000019-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000391-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-000107-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-000094-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000013-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-000771-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-000856-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-000953-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-001038-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-001111-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-001111-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-001184-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-001269-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-001269-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-001342-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-001343-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-001487-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-001560-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-001633-NKW-M-26DY-8HR",
            "item_type": "Service",
            "service_type": "Manpower",
            "is_daily_operation": "Yes",
            "contract_item_category": None
        }
    ],
    "Sea Zen-Sea Zen-2021-06-06": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Qais AlGhanim Group-Qais AlGhanim Group-2020-10-04": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Kuwait Tennis Federation-KTF Security-2021-08-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Kuwait Tennis Federation-PROJ-0198-2021-07-01": [
        {
            "item_code": "SER-CLN-000001-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "Al Babtain Co.-Al-Babtain-2022-03-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-FMG-000294-NKW-M-22DY-9HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "AlRai tv-AlRai TV-2021-09-01": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "German printing and packaging company-German Printing Press-2022-04-01": [
        {
            "item_code": "SER-CLN-000001-NKW-M-26DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        },
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ],
    "IMCO-IMCO-2021-08-09": [
        {
            "item_code": "SER-SEC-000136-NKW-M-30DY-12HR",
            "item_type": "Service",
            "service_type": "Post Schedule",
            "is_daily_operation": None,
            "contract_item_category": None
        }
    ]
}


def update_contract_items():
    """Updates contract items based on embedded data"""
    
    contracts_data = get_contracts_data()
    frappe.db.auto_commit_on_many_writes = True
    
    total_contracts = len(contracts_data)
    total_items_updated = 0
    contracts_not_found = []
    items_not_found = []
    items_per_contract = {}
    
    print(f"Processing {total_contracts} contracts...\n")
    
    for contract_name, items in contracts_data.items():
        try:
            if not frappe.db.exists('Contracts', contract_name):
                contracts_not_found.append(contract_name)
                print(f"⚠ Contract not found: {contract_name}")
                continue
            
            contract_doc = frappe.get_doc('Contracts', contract_name)
            contract_updated = False
            items_updated_count = 0
            
            for item_data in items:
                item_code = item_data.get('item_code')
                
                item_found = False
                for contract_item in contract_doc.items:
                    if contract_item.item_code == item_code:
                        item_found = True
                        
                        # Update Item Type
                        if item_data.get('item_type'):
                            contract_item.item_type = item_data['item_type']
                            contract_updated = True
                        
                        # Update Service Type
                        if item_data.get('service_type'):
                            contract_item.service_type = item_data['service_type']
                            contract_updated = True
                        
                        # Update Is Daily Operation Handled by Us (Select field: Yes/No)
                        if item_data.get('is_daily_operation'):
                            contract_item.is_daily_operation_handled_by_us = item_data['is_daily_operation']
                            contract_updated = True
                        
                        # Update Contract Item Category
                        if item_data.get('contract_item_category'):
                            contract_item.contract_item_category = item_data['contract_item_category']
                            contract_updated = True
                        
                        if contract_updated:
                            items_updated_count += 1
                            total_items_updated += 1
                        
                        break
                
                if not item_found:
                    items_not_found.append(f"{contract_name} - {item_code}")
                    print(f"⚠ Item not found: {item_code} in {contract_name[:50]}")
            
            if contract_updated:
                contract_doc.flags.ignore_validate = True
                contract_doc.flags.ignore_mandatory = True
                contract_doc.save()
                frappe.db.commit()
                items_per_contract[contract_name] = items_updated_count
                print(f"✓ Updated {items_updated_count} items in: {contract_name[:60]}")
            
        except Exception as e:
            print(f"✗ Error processing contract {contract_name}: {str(e)}")
            frappe.db.rollback()
    
    print("\n" + "="*80)
    print("PATCH EXECUTION SUMMARY")
    print("="*80)
    print(f"Total Contracts Processed: {total_contracts}")
    print(f"Total Items Updated: {total_items_updated}")
    print(f"Contracts Not Found: {len(contracts_not_found)}")
    print(f"Items Not Found: {len(items_not_found)}")
    print("="*80 + "\n")
    
    if items_per_contract:
        print("Contracts with multiple items updated:")
        sorted_contracts = sorted(items_per_contract.items(), key=lambda x: x[1], reverse=True)
        for contract, count in sorted_contracts[:10]:
            if count > 1:
                print(f"  {count:2d} items - {contract[:70]}")
        print()
    
    if contracts_not_found:
        print("Contracts Not Found (first 10):")
        for contract in contracts_not_found[:10]:
            print(f"  - {contract}")
        print()
    
    if items_not_found:
        print("Items Not Found (first 10):")
        for item in items_not_found[:10]:
            print(f"  - {item}")
        print()
    
    print("="*80)
    print("✓ Patch execution completed!")
    print("="*80 + "\n")