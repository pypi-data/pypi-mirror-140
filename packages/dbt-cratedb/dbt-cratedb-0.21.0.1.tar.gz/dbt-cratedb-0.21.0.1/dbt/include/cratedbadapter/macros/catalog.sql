{% macro cratedbadapter__alter_column_type(relation, column_name, new_column_type) -%}
  {#
    1. Create a new column (w/ temp name and correct type)
    2. Copy data over to it
    3. XXX Drop the existing column (cascade!) XXX
    4. Rename the new column to existing column
  #}
  {%- set tmp_column = column_name + "__dbt_alter" -%}

  {% call statement('alter_column_type') %}
    alter table {{ relation }} add column {{ adapter.quote(tmp_column) }} {{ new_column_type }};
    update {{ relation }} set {{ adapter.quote(tmp_column) }} = {{ adapter.quote(column_name) }};
    alter table {{ relation }} drop column {{ adapter.quote(column_name) }};
    alter table {{ relation }} rename column {{ adapter.quote(tmp_column) }} to {{ adapter.quote(column_name) }}
  {% endcall %}

{% endmacro %}

{% macro default__drop_schema(relation) -%}
  {%- call statement('drop_schema') -%}
    commit;
  {% endcall %}
{% endmacro %}

{% macro cratedbadapter__get_catalog(information_schema, schemas) -%}

  {%- call statement('catalog', fetch_result=True) -%}

    select
        sch.nspname as table_schema,
        tbl.relname as table_name,
        case tbl.relkind
            when 'v' then 'VIEW'
            else 'BASE TABLE'
        end as table_type,
        tbl_desc.description as table_comment,
        col.attname as column_name,
        col.attnum as column_index,
        pg_catalog.format_type(col.atttypid, col.atttypmod) as column_type,
        col_desc.description as column_comment,
        pg_get_userbyid(tbl.relowner) as table_owner

    from pg_catalog.pg_namespace sch
    join pg_catalog.pg_class tbl on tbl.relnamespace = sch.oid
    join pg_catalog.pg_attribute col on col.attrelid = tbl.oid
    left outer join pg_catalog.pg_description tbl_desc on (tbl_desc.objoid = tbl.oid and tbl_desc.objsubid = 0)
    left outer join pg_catalog.pg_description col_desc on (col_desc.objoid = tbl.oid and col_desc.objsubid = col.attnum)

    where (
        {%- for schema in schemas -%}
          upper(sch.nspname) = upper('{{ schema }}'){%- if not loop.last %} or {% endif -%}
        {%- endfor -%}
      )
      and tbl.relpersistence = 'p'
      and tbl.relkind in ('r', 'v', 'f', 'p')
      and col.attnum > 0
      and not col.attisdropped
      order by sch.nspname, tbl.relname, col.attnum

  {%- endcall -%}

  {{ return(load_result('catalog').table) }}

{%- endmacro %}


