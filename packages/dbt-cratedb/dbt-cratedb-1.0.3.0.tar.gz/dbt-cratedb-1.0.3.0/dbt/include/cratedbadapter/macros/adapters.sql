
{% macro cratedbadapter__create_table_as(temporary, relation, sql) -%}

  {%- call statement('check_relation_exists', fetch_result=True) -%}
    select count(*) from "information_schema"."tables" where table_name='{{ relation.identifier }}' and table_schema='{{ relation.schema }}';
  {% endcall %}
  {% set relation_exists = load_result('check_relation_exists') %}
  {% if relation_exists['data'][0][0] == 0 %}
    create table {{ relation }}
      as (
        {{ sql }}
      );
  {% else %}
    commit;
  {% endif %}

{%- endmacro %}

{% macro cratedbadapter__check_schema_exists(information_schema, schema) -%}
  {#
    On CrateDB, schemas are created implicitly according to the name used.
    If a schema does not exist, CrateDB create it automatically.
  #}
  {% call statement('check_schema_exists', fetch_result=True, auto_begin=False) %}
    select 1;
  {% endcall %}
  {{ return(load_result('check_schema_exists').table) }}
{% endmacro %}

{% macro cratedbadapter__get_columns_in_relation(relation) -%}
  {% call statement('get_columns_in_relation', fetch_result=True) %}
      select
          column_name,
          data_type,
          character_maximum_length,
          numeric_precision,
          numeric_scale

      from {{ relation.information_schema('columns') }}
      where table_name = '{{ relation.identifier }}'
        {% if relation.schema %}
        and table_schema = '{{ relation.schema }}'
        {% endif %}
      order by ordinal_position

  {% endcall %}
  {% set table = load_result('get_columns_in_relation').table %}
  {{ return(sql_convert_columns_in_relation(table)) }}
{% endmacro %}

{% macro cratedbadapter__list_relations_without_caching(schema_relation) %}
  {% call statement('list_relations_without_caching', fetch_result=True) -%}
    select
      '{{ schema_relation.database }}' as database,
      table_name as name,
      table_schema as schema,
      'table' as type
    from information_schema.tables
    where table_schema ilike '{{ schema_relation.schema }}'
    union all
    select
      '{{ schema_relation.database }}' as database,
      table_name as name,
      table_schema as schema,
      'view' as type
    from information_schema.views
    where table_schema ilike '{{ schema_relation.schema }}'
  {% endcall %}
  {{ return(load_result('list_relations_without_caching').table) }}
{% endmacro %}

{% macro cratedbadapter__current_timestamp() -%}
  now()
{%- endmacro %}


{% macro cratedbadapter__create_view_as(relation, sql) -%}
  create table {{ relation }} as
    {{ sql }};
{% endmacro %}


{% macro cratedbadapter__rename_relation(from_relation, to_relation) -%}
  {% call statement('rename_relation') -%}
    alter table {{ from_relation }} rename to {{ to_relation.name }}
  {%- endcall %}
{% endmacro %}

{% macro cratedbadapter__create_schema(relation) -%}
  {%- call statement('create_schema') -%}
    commit;
  {%- endcall -%}
{% endmacro %}

{% macro dbt_macro__create_schema(relation) -%}
  {%- call statement('create_schema') -%}
    commit;
  {%- endcall -%}
{% endmacro %}

