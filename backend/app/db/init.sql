-- =============================================================================
-- A07 数据底座 DDL (PostgreSQL 14+)
-- 10 张核心表：维度 2 + 生产 2 + 质量 2 + 设备 2 + 库存 3 - 1 共享
-- 跨平台：使用标准 SQL，PG 14+ 兼容
-- =============================================================================

-- 启用扩展
CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- gen_random_uuid()

-- =============================================================================
-- 公共维度
-- =============================================================================

-- 产品维度
DROP TABLE IF EXISTS dim_product CASCADE;
CREATE TABLE dim_product (
    product_code   VARCHAR(32) PRIMARY KEY,
    product_name   VARCHAR(128) NOT NULL,
    category       VARCHAR(32) NOT NULL,
    spec           VARCHAR(128),
    unit           VARCHAR(16) DEFAULT '件',
    created_at     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_dim_product_category ON dim_product (category);

COMMENT ON TABLE dim_product IS '产品维度';

-- 产线维度
DROP TABLE IF EXISTS dim_line CASCADE;
CREATE TABLE dim_line (
    line_code            VARCHAR(32) PRIMARY KEY,
    line_name            VARCHAR(128) NOT NULL,
    workshop             VARCHAR(64) NOT NULL,
    capacity_per_shift   INTEGER DEFAULT 1000,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE dim_line IS '产线维度';
COMMENT ON COLUMN dim_line.capacity_per_shift IS '每班次产能';

-- =============================================================================
-- 生产域
-- =============================================================================

DROP TABLE IF EXISTS production_workorder CASCADE;
CREATE TABLE production_workorder (
    workorder_id   VARCHAR(32) PRIMARY KEY,
    product_code   VARCHAR(32) NOT NULL REFERENCES dim_product(product_code),
    line_code      VARCHAR(32) NOT NULL REFERENCES dim_line(line_code),
    plan_qty       INTEGER NOT NULL,
    actual_qty     INTEGER DEFAULT 0,
    start_date     DATE NOT NULL,
    end_date       DATE,
    status         VARCHAR(16) DEFAULT '进行中',
    created_at     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_wo_product ON production_workorder (product_code);
CREATE INDEX ix_wo_line ON production_workorder (line_code);
CREATE INDEX ix_wo_start_date ON production_workorder (start_date);
CREATE INDEX ix_wo_status ON production_workorder (status);

COMMENT ON TABLE production_workorder IS '生产工单';
COMMENT ON COLUMN production_workorder.status IS '状态：进行中/已完成/已取消';

DROP TABLE IF EXISTS production_process CASCADE;
CREATE TABLE production_process (
    id              SERIAL PRIMARY KEY,
    workorder_id    VARCHAR(32) NOT NULL REFERENCES production_workorder(workorder_id),
    process_code    VARCHAR(32) NOT NULL,
    process_name    VARCHAR(64) NOT NULL,
    total_qty       INTEGER NOT NULL,
    qualified_qty   INTEGER NOT NULL,
    record_date     DATE NOT NULL,
    operator        VARCHAR(32),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_process_workorder ON production_process (workorder_id);
CREATE INDEX ix_process_code ON production_process (process_code);
CREATE INDEX ix_process_record_date ON production_process (record_date);
CREATE INDEX ix_process_workorder_process ON production_process (workorder_id, process_code);

COMMENT ON TABLE production_process IS '工序产量';
COMMENT ON COLUMN production_process.total_qty IS '投入数量';
COMMENT ON COLUMN production_process.qualified_qty IS '合格数量';

-- =============================================================================
-- 质量域
-- =============================================================================

DROP TABLE IF EXISTS quality_inspection CASCADE;
CREATE TABLE quality_inspection (
    inspection_id     VARCHAR(32) PRIMARY KEY,
    workorder_id      VARCHAR(32) REFERENCES production_workorder(workorder_id),
    product_code      VARCHAR(32) NOT NULL REFERENCES dim_product(product_code),
    batch_no          VARCHAR(32) NOT NULL,
    inspected_qty     INTEGER NOT NULL,
    passed_qty        INTEGER NOT NULL,
    inspection_date   DATE NOT NULL,
    inspector         VARCHAR(32),
    result            VARCHAR(16) DEFAULT '合格',
    created_at        TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_inspection_product ON quality_inspection (product_code);
CREATE INDEX ix_inspection_batch ON quality_inspection (batch_no);
CREATE INDEX ix_inspection_date ON quality_inspection (inspection_date);
CREATE INDEX ix_inspection_result ON quality_inspection (result);
CREATE INDEX ix_inspection_product_date ON quality_inspection (product_code, inspection_date);

COMMENT ON TABLE quality_inspection IS '质量检验';
COMMENT ON COLUMN quality_inspection.result IS '合格/不合格';

DROP TABLE IF EXISTS quality_defect CASCADE;
CREATE TABLE quality_defect (
    defect_id       VARCHAR(32) PRIMARY KEY,
    inspection_id   VARCHAR(32) NOT NULL REFERENCES quality_inspection(inspection_id),
    product_code    VARCHAR(32) NOT NULL REFERENCES dim_product(product_code),
    defect_type     VARCHAR(32) NOT NULL,
    defect_qty      INTEGER NOT NULL,
    severity        VARCHAR(16) DEFAULT '轻微',
    defect_date     DATE NOT NULL,
    cause           VARCHAR(256),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_defect_inspection ON quality_defect (inspection_id);
CREATE INDEX ix_defect_product ON quality_defect (product_code);
CREATE INDEX ix_defect_type ON quality_defect (defect_type);
CREATE INDEX ix_defect_date ON quality_defect (defect_date);

COMMENT ON TABLE quality_defect IS '质量缺陷';
COMMENT ON COLUMN quality_defect.severity IS '轻微/严重/致命';

-- =============================================================================
-- 设备域
-- =============================================================================

DROP TABLE IF EXISTS equipment CASCADE;
CREATE TABLE equipment (
    equipment_code   VARCHAR(32) PRIMARY KEY,
    equipment_name   VARCHAR(128) NOT NULL,
    equipment_type   VARCHAR(32) NOT NULL,
    line_code        VARCHAR(32) REFERENCES dim_line(line_code),
    status           VARCHAR(16) DEFAULT '运行中',
    install_date     DATE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_equipment_type ON equipment (equipment_type);
CREATE INDEX ix_equipment_status ON equipment (status);

COMMENT ON TABLE equipment IS '设备主数据';

DROP TABLE IF EXISTS equipment_downtime CASCADE;
CREATE TABLE equipment_downtime (
    id                 SERIAL PRIMARY KEY,
    equipment_code     VARCHAR(32) NOT NULL REFERENCES equipment(equipment_code),
    downtime_date      DATE NOT NULL,
    start_time         VARCHAR(8) NOT NULL,
    end_time           VARCHAR(8) NOT NULL,
    downtime_minutes   INTEGER NOT NULL,
    reason             VARCHAR(64) NOT NULL,
    impact_qty         INTEGER DEFAULT 0,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_downtime_equipment ON equipment_downtime (equipment_code);
CREATE INDEX ix_downtime_date ON equipment_downtime (downtime_date);
CREATE INDEX ix_downtime_reason ON equipment_downtime (reason);
CREATE INDEX ix_downtime_equipment_date ON equipment_downtime (equipment_code, downtime_date);

COMMENT ON TABLE equipment_downtime IS '设备停机';

-- =============================================================================
-- 库存域
-- =============================================================================

DROP TABLE IF EXISTS warehouse CASCADE;
CREATE TABLE warehouse (
    warehouse_code   VARCHAR(32) PRIMARY KEY,
    warehouse_name   VARCHAR(128) NOT NULL,
    location         VARCHAR(128) DEFAULT '',
    capacity         INTEGER DEFAULT 10000,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE warehouse IS '仓库';

DROP TABLE IF EXISTS material CASCADE;
CREATE TABLE material (
    material_code   VARCHAR(32) PRIMARY KEY,
    material_name   VARCHAR(128) NOT NULL,
    category        VARCHAR(32) NOT NULL,
    spec            VARCHAR(128),
    unit            VARCHAR(16) DEFAULT '件',
    safety_stock    INTEGER DEFAULT 100,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_material_category ON material (category);

COMMENT ON TABLE material IS '物料主数据';
COMMENT ON COLUMN material.safety_stock IS '安全库存';

DROP TABLE IF EXISTS inventory_balance CASCADE;
CREATE TABLE inventory_balance (
    id              SERIAL PRIMARY KEY,
    material_code   VARCHAR(32) NOT NULL REFERENCES material(material_code),
    warehouse_code  VARCHAR(32) NOT NULL REFERENCES warehouse(warehouse_code),
    balance_date    DATE NOT NULL,
    balance_qty     INTEGER NOT NULL,
    in_qty          INTEGER DEFAULT 0,
    out_qty         INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_balance_material ON inventory_balance (material_code);
CREATE INDEX ix_balance_warehouse ON inventory_balance (warehouse_code);
CREATE INDEX ix_balance_date ON inventory_balance (balance_date);
CREATE INDEX ix_balance_material_warehouse_date ON inventory_balance (material_code, warehouse_code, balance_date);

COMMENT ON TABLE inventory_balance IS '库存余额';
