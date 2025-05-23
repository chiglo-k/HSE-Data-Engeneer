PGDMP                      |         	   oved_test    17.2    17.0 s    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                           false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                           false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                           false            �           1262    16536 	   oved_test    DATABASE     }   CREATE DATABASE oved_test WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'Russian_Russia.1251';
    DROP DATABASE oved_test;
                     chiga    false                        2615    2200    public    SCHEMA        CREATE SCHEMA public;
    DROP SCHEMA public;
                     pg_database_owner    false            �           0    0    SCHEMA public    COMMENT     6   COMMENT ON SCHEMA public IS 'standard public schema';
                        pg_database_owner    false    4            �            1255    16974    add_to_export_holder()    FUNCTION     �  CREATE FUNCTION public.add_to_export_holder() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Check if the operation type is 'экспорт'
    IF NEW.operation_type = 'экспорт' THEN
        INSERT INTO export_holder (unique_conosament, unique_product, unique_package)
        VALUES (NEW.conosament, NEW.production, NEW.package)
        ON CONFLICT (unique_conosament, unique_product, unique_package) DO NOTHING;
    END IF;
    RETURN NEW;
END;
$$;
 -   DROP FUNCTION public.add_to_export_holder();
       public               chiga    false    4            �            1255    16883    add_to_inner_holder()    FUNCTION       CREATE FUNCTION public.add_to_inner_holder() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Check if the operation type is 'внутренний рынок'
    IF NEW.operation_type = 'внутренний рынок' THEN
        INSERT INTO inner_holder (unique_conosament, unique_product, unique_package)
        VALUES (NEW.conosament, NEW.production, NEW.package)
        ON CONFLICT (unique_conosament, unique_product, unique_package) DO NOTHING;
    END IF;
    RETURN NEW;
END;
$$;
 ,   DROP FUNCTION public.add_to_inner_holder();
       public               chiga    false    4            �            1255    16900    add_to_storage_holder()    FUNCTION     �  CREATE FUNCTION public.add_to_storage_holder() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Check if the operation type is 'хранение'
    IF NEW.operation_type = 'хранение' THEN
        INSERT INTO storage_holder (unique_conosament, unique_product, unique_package)
        VALUES (NEW.conosament, NEW.production, NEW.package)
        ON CONFLICT (unique_conosament, unique_product, unique_package) DO NOTHING;
    END IF;
    RETURN NEW;
END;
$$;
 .   DROP FUNCTION public.add_to_storage_holder();
       public               chiga    false    4            �            1255    17027    total_products()    FUNCTION     ?  CREATE FUNCTION public.total_products() RETURNS TABLE(production text, total_places integer, total_products double precision)
    LANGUAGE plpgsql
    AS $$
begin
	return query
	select c.production, sum(c.places)::integer, sum(c.total_net)::double precision
	from conosaments c 
	group by c.production;
end;
$$;
 '   DROP FUNCTION public.total_products();
       public               chiga    false    4            �            1259    16668    agreement_info    TABLE     �   CREATE TABLE public.agreement_info (
    number_unique text NOT NULL,
    date_of_begin date,
    seller text,
    buyer text
);
 "   DROP TABLE public.agreement_info;
       public         heap r       chiga    false    4            �            1259    16640    clients_export    TABLE     r   CREATE TABLE public.clients_export (
    name_short text NOT NULL,
    name_full text NOT NULL,
    info jsonb
);
 "   DROP TABLE public.clients_export;
       public         heap r       chiga    false    4            �            1259    16633    clients_rus    TABLE     o   CREATE TABLE public.clients_rus (
    name_short text NOT NULL,
    name_full text NOT NULL,
    info jsonb
);
    DROP TABLE public.clients_rus;
       public         heap r       chiga    false    4            �            1259    16626    company_rus    TABLE     �   CREATE TABLE public.company_rus (
    name_short text NOT NULL,
    name_full text NOT NULL,
    eng_name text NOT NULL,
    info jsonb
);
    DROP TABLE public.company_rus;
       public         heap r       chiga    false    4            �            1259    16800    conosaments    TABLE     �  CREATE TABLE public.conosaments (
    id integer NOT NULL,
    route_number text NOT NULL,
    conosament text NOT NULL,
    date timestamp without time zone,
    vessel text NOT NULL,
    transport text NOT NULL,
    production text NOT NULL,
    package real NOT NULL,
    places integer NOT NULL,
    total_net double precision GENERATED ALWAYS AS ((package * (places)::double precision)) STORED,
    operation_type text NOT NULL,
    company text
);
    DROP TABLE public.conosaments;
       public         heap r       chiga    false    4            �            1259    16799    conosaments_id_seq    SEQUENCE     �   CREATE SEQUENCE public.conosaments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 )   DROP SEQUENCE public.conosaments_id_seq;
       public               chiga    false    4    226            �           0    0    conosaments_id_seq    SEQUENCE OWNED BY     I   ALTER SEQUENCE public.conosaments_id_seq OWNED BY public.conosaments.id;
          public               chiga    false    225            �            1259    16977    export    TABLE       CREATE TABLE public.export (
    id integer NOT NULL,
    contract_num text NOT NULL,
    agreement_num text NOT NULL,
    data timestamp without time zone NOT NULL,
    bl_num text NOT NULL,
    invoice text NOT NULL,
    product text NOT NULL,
    package real NOT NULL,
    place integer NOT NULL,
    total_value double precision GENERATED ALWAYS AS ((package * (place)::double precision)) STORED,
    price money NOT NULL,
    total_amount money GENERATED ALWAYS AS (((package * (place)::double precision) * price)) STORED
);
    DROP TABLE public.export;
       public         heap r       chiga    false    4            �            1259    16960    export_holder    TABLE     �   CREATE TABLE public.export_holder (
    id integer NOT NULL,
    unique_conosament text NOT NULL,
    unique_product text NOT NULL,
    unique_package real NOT NULL
);
 !   DROP TABLE public.export_holder;
       public         heap r       chiga    false    4            �            1259    16959    export_holder_id_seq    SEQUENCE     �   CREATE SEQUENCE public.export_holder_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.export_holder_id_seq;
       public               chiga    false    236    4            �           0    0    export_holder_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.export_holder_id_seq OWNED BY public.export_holder.id;
          public               chiga    false    235            �            1259    16976    export_id_seq    SEQUENCE     �   CREATE SEQUENCE public.export_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 $   DROP SEQUENCE public.export_id_seq;
       public               chiga    false    4    238            �           0    0    export_id_seq    SEQUENCE OWNED BY     ?   ALTER SEQUENCE public.export_id_seq OWNED BY public.export.id;
          public               chiga    false    237            �            1259    16830    inner_holder    TABLE     �   CREATE TABLE public.inner_holder (
    id integer NOT NULL,
    unique_conosament text NOT NULL,
    unique_product text NOT NULL,
    unique_package real NOT NULL
);
     DROP TABLE public.inner_holder;
       public         heap r       chiga    false    4            �            1259    16829    inner_holder_id_seq    SEQUENCE     �   CREATE SEQUENCE public.inner_holder_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 *   DROP SEQUENCE public.inner_holder_id_seq;
       public               chiga    false    228    4            �           0    0    inner_holder_id_seq    SEQUENCE OWNED BY     K   ALTER SEQUENCE public.inner_holder_id_seq OWNED BY public.inner_holder.id;
          public               chiga    false    227            �            1259    16903    inner_market    TABLE     �  CREATE TABLE public.inner_market (
    id integer NOT NULL,
    conosament_num text NOT NULL,
    date timestamp without time zone NOT NULL,
    num_agreement text NOT NULL,
    client text NOT NULL,
    production text NOT NULL,
    package real NOT NULL,
    places integer NOT NULL,
    total_net double precision GENERATED ALWAYS AS ((package * (places)::double precision)) STORED,
    price money NOT NULL,
    amount money GENERATED ALWAYS AS (((package * (places)::double precision) * price)) STORED
);
     DROP TABLE public.inner_market;
       public         heap r       chiga    false    4            �            1259    16902    inner_market_id_seq    SEQUENCE     �   CREATE SEQUENCE public.inner_market_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 *   DROP SEQUENCE public.inner_market_id_seq;
       public               chiga    false    232    4            �           0    0    inner_market_id_seq    SEQUENCE OWNED BY     K   ALTER SEQUENCE public.inner_market_id_seq OWNED BY public.inner_market.id;
          public               chiga    false    231            �            1259    16716 
   operations    TABLE     E   CREATE TABLE public.operations (
    name_operation text NOT NULL
);
    DROP TABLE public.operations;
       public         heap r       chiga    false    4            �            1259    16598    productions    TABLE     �   CREATE TABLE public.productions (
    product_name text NOT NULL,
    product_name_eng text NOT NULL,
    package real NOT NULL
);
    DROP TABLE public.productions;
       public         heap r       chiga    false    4            �            1259    16934    storage    TABLE       CREATE TABLE public.storage (
    id integer NOT NULL,
    contract_num text NOT NULL,
    agreement_num text NOT NULL,
    data timestamp without time zone NOT NULL,
    bl_num text NOT NULL,
    invoice text NOT NULL,
    product text NOT NULL,
    package real NOT NULL,
    place integer NOT NULL,
    total_value double precision GENERATED ALWAYS AS ((package * (place)::double precision)) STORED,
    price money NOT NULL,
    total_amount money GENERATED ALWAYS AS (((package * (place)::double precision) * price)) STORED
);
    DROP TABLE public.storage;
       public         heap r       chiga    false    4            �            1259    16886    storage_holder    TABLE     �   CREATE TABLE public.storage_holder (
    id integer NOT NULL,
    unique_conosament text NOT NULL,
    unique_product text NOT NULL,
    unique_package real NOT NULL
);
 "   DROP TABLE public.storage_holder;
       public         heap r       chiga    false    4            �            1259    16885    storage_holder_id_seq    SEQUENCE     �   CREATE SEQUENCE public.storage_holder_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ,   DROP SEQUENCE public.storage_holder_id_seq;
       public               chiga    false    4    230            �           0    0    storage_holder_id_seq    SEQUENCE OWNED BY     O   ALTER SEQUENCE public.storage_holder_id_seq OWNED BY public.storage_holder.id;
          public               chiga    false    229            �            1259    16933    storage_id_seq    SEQUENCE     �   CREATE SEQUENCE public.storage_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 %   DROP SEQUENCE public.storage_id_seq;
       public               chiga    false    4    234            �           0    0    storage_id_seq    SEQUENCE OWNED BY     A   ALTER SEQUENCE public.storage_id_seq OWNED BY public.storage.id;
          public               chiga    false    233            �            1259    16619 
   transports    TABLE     v   CREATE TABLE public.transports (
    name_rus text NOT NULL,
    name_eng text NOT NULL,
    code_transports jsonb
);
    DROP TABLE public.transports;
       public         heap r       chiga    false    4            �            1259    16612    vessels    TABLE     h   CREATE TABLE public.vessels (
    name_rus text NOT NULL,
    name_eng text NOT NULL,
    code jsonb
);
    DROP TABLE public.vessels;
       public         heap r       chiga    false    4            �           2604    16803    conosaments id    DEFAULT     p   ALTER TABLE ONLY public.conosaments ALTER COLUMN id SET DEFAULT nextval('public.conosaments_id_seq'::regclass);
 =   ALTER TABLE public.conosaments ALTER COLUMN id DROP DEFAULT;
       public               chiga    false    225    226    226            �           2604    16980 	   export id    DEFAULT     f   ALTER TABLE ONLY public.export ALTER COLUMN id SET DEFAULT nextval('public.export_id_seq'::regclass);
 8   ALTER TABLE public.export ALTER COLUMN id DROP DEFAULT;
       public               chiga    false    237    238    238            �           2604    16963    export_holder id    DEFAULT     t   ALTER TABLE ONLY public.export_holder ALTER COLUMN id SET DEFAULT nextval('public.export_holder_id_seq'::regclass);
 ?   ALTER TABLE public.export_holder ALTER COLUMN id DROP DEFAULT;
       public               chiga    false    236    235    236            �           2604    16833    inner_holder id    DEFAULT     r   ALTER TABLE ONLY public.inner_holder ALTER COLUMN id SET DEFAULT nextval('public.inner_holder_id_seq'::regclass);
 >   ALTER TABLE public.inner_holder ALTER COLUMN id DROP DEFAULT;
       public               chiga    false    228    227    228            �           2604    16906    inner_market id    DEFAULT     r   ALTER TABLE ONLY public.inner_market ALTER COLUMN id SET DEFAULT nextval('public.inner_market_id_seq'::regclass);
 >   ALTER TABLE public.inner_market ALTER COLUMN id DROP DEFAULT;
       public               chiga    false    232    231    232            �           2604    16937 
   storage id    DEFAULT     h   ALTER TABLE ONLY public.storage ALTER COLUMN id SET DEFAULT nextval('public.storage_id_seq'::regclass);
 9   ALTER TABLE public.storage ALTER COLUMN id DROP DEFAULT;
       public               chiga    false    234    233    234            �           2604    16889    storage_holder id    DEFAULT     v   ALTER TABLE ONLY public.storage_holder ALTER COLUMN id SET DEFAULT nextval('public.storage_holder_id_seq'::regclass);
 @   ALTER TABLE public.storage_holder ALTER COLUMN id DROP DEFAULT;
       public               chiga    false    230    229    230            �          0    16668    agreement_info 
   TABLE DATA           U   COPY public.agreement_info (number_unique, date_of_begin, seller, buyer) FROM stdin;
    public               chiga    false    223   �       �          0    16640    clients_export 
   TABLE DATA           E   COPY public.clients_export (name_short, name_full, info) FROM stdin;
    public               chiga    false    222   z�       �          0    16633    clients_rus 
   TABLE DATA           B   COPY public.clients_rus (name_short, name_full, info) FROM stdin;
    public               chiga    false    221   l�       �          0    16626    company_rus 
   TABLE DATA           L   COPY public.company_rus (name_short, name_full, eng_name, info) FROM stdin;
    public               chiga    false    220   ��       �          0    16800    conosaments 
   TABLE DATA           �   COPY public.conosaments (id, route_number, conosament, date, vessel, transport, production, package, places, operation_type, company) FROM stdin;
    public               chiga    false    226   x�       �          0    16977    export 
   TABLE DATA           x   COPY public.export (id, contract_num, agreement_num, data, bl_num, invoice, product, package, place, price) FROM stdin;
    public               chiga    false    238   E�       �          0    16960    export_holder 
   TABLE DATA           ^   COPY public.export_holder (id, unique_conosament, unique_product, unique_package) FROM stdin;
    public               chiga    false    236   ��       �          0    16830    inner_holder 
   TABLE DATA           ]   COPY public.inner_holder (id, unique_conosament, unique_product, unique_package) FROM stdin;
    public               chiga    false    228   V�       �          0    16903    inner_market 
   TABLE DATA           {   COPY public.inner_market (id, conosament_num, date, num_agreement, client, production, package, places, price) FROM stdin;
    public               chiga    false    232          �          0    16716 
   operations 
   TABLE DATA           4   COPY public.operations (name_operation) FROM stdin;
    public               chiga    false    224   ��       �          0    16598    productions 
   TABLE DATA           N   COPY public.productions (product_name, product_name_eng, package) FROM stdin;
    public               chiga    false    217   �       �          0    16934    storage 
   TABLE DATA           y   COPY public.storage (id, contract_num, agreement_num, data, bl_num, invoice, product, package, place, price) FROM stdin;
    public               chiga    false    234   =�       �          0    16886    storage_holder 
   TABLE DATA           _   COPY public.storage_holder (id, unique_conosament, unique_product, unique_package) FROM stdin;
    public               chiga    false    230   �       �          0    16619 
   transports 
   TABLE DATA           I   COPY public.transports (name_rus, name_eng, code_transports) FROM stdin;
    public               chiga    false    219   M�       �          0    16612    vessels 
   TABLE DATA           ;   COPY public.vessels (name_rus, name_eng, code) FROM stdin;
    public               chiga    false    218   �       �           0    0    conosaments_id_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('public.conosaments_id_seq', 18, true);
          public               chiga    false    225            �           0    0    export_holder_id_seq    SEQUENCE SET     B   SELECT pg_catalog.setval('public.export_holder_id_seq', 4, true);
          public               chiga    false    235            �           0    0    export_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('public.export_id_seq', 3, true);
          public               chiga    false    237            �           0    0    inner_holder_id_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('public.inner_holder_id_seq', 6, true);
          public               chiga    false    227            �           0    0    inner_market_id_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('public.inner_market_id_seq', 4, true);
          public               chiga    false    231            �           0    0    storage_holder_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.storage_holder_id_seq', 6, true);
          public               chiga    false    229            �           0    0    storage_id_seq    SEQUENCE SET     <   SELECT pg_catalog.setval('public.storage_id_seq', 2, true);
          public               chiga    false    233            �           2606    16674 "   agreement_info agreement_info_pkey 
   CONSTRAINT     k   ALTER TABLE ONLY public.agreement_info
    ADD CONSTRAINT agreement_info_pkey PRIMARY KEY (number_unique);
 L   ALTER TABLE ONLY public.agreement_info DROP CONSTRAINT agreement_info_pkey;
       public                 chiga    false    223            �           2606    16646 "   clients_export clients_export_pkey 
   CONSTRAINT     h   ALTER TABLE ONLY public.clients_export
    ADD CONSTRAINT clients_export_pkey PRIMARY KEY (name_short);
 L   ALTER TABLE ONLY public.clients_export DROP CONSTRAINT clients_export_pkey;
       public                 chiga    false    222            �           2606    16639    clients_rus clients_rus_pkey 
   CONSTRAINT     b   ALTER TABLE ONLY public.clients_rus
    ADD CONSTRAINT clients_rus_pkey PRIMARY KEY (name_short);
 F   ALTER TABLE ONLY public.clients_rus DROP CONSTRAINT clients_rus_pkey;
       public                 chiga    false    221            �           2606    16632    company_rus company_rus_pkey 
   CONSTRAINT     b   ALTER TABLE ONLY public.company_rus
    ADD CONSTRAINT company_rus_pkey PRIMARY KEY (name_short);
 F   ALTER TABLE ONLY public.company_rus DROP CONSTRAINT company_rus_pkey;
       public                 chiga    false    220            �           2606    16808    conosaments conosaments_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY public.conosaments
    ADD CONSTRAINT conosaments_pkey PRIMARY KEY (id);
 F   ALTER TABLE ONLY public.conosaments DROP CONSTRAINT conosaments_pkey;
       public                 chiga    false    226                       2606    16967     export_holder export_holder_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.export_holder
    ADD CONSTRAINT export_holder_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.export_holder DROP CONSTRAINT export_holder_pkey;
       public                 chiga    false    236                       2606    16969 1   export_holder export_holder_unique_conosament_key 
   CONSTRAINT     y   ALTER TABLE ONLY public.export_holder
    ADD CONSTRAINT export_holder_unique_conosament_key UNIQUE (unique_conosament);
 [   ALTER TABLE ONLY public.export_holder DROP CONSTRAINT export_holder_unique_conosament_key;
       public                 chiga    false    236                       2606    16973 .   export_holder export_holder_unique_package_key 
   CONSTRAINT     s   ALTER TABLE ONLY public.export_holder
    ADD CONSTRAINT export_holder_unique_package_key UNIQUE (unique_package);
 X   ALTER TABLE ONLY public.export_holder DROP CONSTRAINT export_holder_unique_package_key;
       public                 chiga    false    236                       2606    16971 .   export_holder export_holder_unique_product_key 
   CONSTRAINT     s   ALTER TABLE ONLY public.export_holder
    ADD CONSTRAINT export_holder_unique_product_key UNIQUE (unique_product);
 X   ALTER TABLE ONLY public.export_holder DROP CONSTRAINT export_holder_unique_product_key;
       public                 chiga    false    236            !           2606    16986    export export_pkey 
   CONSTRAINT     P   ALTER TABLE ONLY public.export
    ADD CONSTRAINT export_pkey PRIMARY KEY (id);
 <   ALTER TABLE ONLY public.export DROP CONSTRAINT export_pkey;
       public                 chiga    false    238            �           2606    16837    inner_holder inner_holder_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.inner_holder
    ADD CONSTRAINT inner_holder_pkey PRIMARY KEY (id);
 H   ALTER TABLE ONLY public.inner_holder DROP CONSTRAINT inner_holder_pkey;
       public                 chiga    false    228                       2606    16912    inner_market inner_market_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.inner_market
    ADD CONSTRAINT inner_market_pkey PRIMARY KEY (id);
 H   ALTER TABLE ONLY public.inner_market DROP CONSTRAINT inner_market_pkey;
       public                 chiga    false    232            �           2606    16722    operations operations_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.operations
    ADD CONSTRAINT operations_pkey PRIMARY KEY (name_operation);
 D   ALTER TABLE ONLY public.operations DROP CONSTRAINT operations_pkey;
       public                 chiga    false    224            �           2606    16604    productions productions_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.productions
    ADD CONSTRAINT productions_pkey PRIMARY KEY (product_name);
 F   ALTER TABLE ONLY public.productions DROP CONSTRAINT productions_pkey;
       public                 chiga    false    217            	           2606    16893 "   storage_holder storage_holder_pkey 
   CONSTRAINT     `   ALTER TABLE ONLY public.storage_holder
    ADD CONSTRAINT storage_holder_pkey PRIMARY KEY (id);
 L   ALTER TABLE ONLY public.storage_holder DROP CONSTRAINT storage_holder_pkey;
       public                 chiga    false    230                       2606    16895 3   storage_holder storage_holder_unique_conosament_key 
   CONSTRAINT     {   ALTER TABLE ONLY public.storage_holder
    ADD CONSTRAINT storage_holder_unique_conosament_key UNIQUE (unique_conosament);
 ]   ALTER TABLE ONLY public.storage_holder DROP CONSTRAINT storage_holder_unique_conosament_key;
       public                 chiga    false    230                       2606    16899 0   storage_holder storage_holder_unique_package_key 
   CONSTRAINT     u   ALTER TABLE ONLY public.storage_holder
    ADD CONSTRAINT storage_holder_unique_package_key UNIQUE (unique_package);
 Z   ALTER TABLE ONLY public.storage_holder DROP CONSTRAINT storage_holder_unique_package_key;
       public                 chiga    false    230                       2606    16897 0   storage_holder storage_holder_unique_product_key 
   CONSTRAINT     u   ALTER TABLE ONLY public.storage_holder
    ADD CONSTRAINT storage_holder_unique_product_key UNIQUE (unique_product);
 Z   ALTER TABLE ONLY public.storage_holder DROP CONSTRAINT storage_holder_unique_product_key;
       public                 chiga    false    230                       2606    16943    storage storage_pkey 
   CONSTRAINT     R   ALTER TABLE ONLY public.storage
    ADD CONSTRAINT storage_pkey PRIMARY KEY (id);
 >   ALTER TABLE ONLY public.storage DROP CONSTRAINT storage_pkey;
       public                 chiga    false    234            �           2606    16625    transports transports_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.transports
    ADD CONSTRAINT transports_pkey PRIMARY KEY (name_rus);
 D   ALTER TABLE ONLY public.transports DROP CONSTRAINT transports_pkey;
       public                 chiga    false    219                       2606    16849    inner_holder unique_conosament 
   CONSTRAINT     f   ALTER TABLE ONLY public.inner_holder
    ADD CONSTRAINT unique_conosament UNIQUE (unique_conosament);
 H   ALTER TABLE ONLY public.inner_holder DROP CONSTRAINT unique_conosament;
       public                 chiga    false    228                       2606    17021 .   inner_holder unique_conosament_product_package 
   CONSTRAINT     �   ALTER TABLE ONLY public.inner_holder
    ADD CONSTRAINT unique_conosament_product_package UNIQUE (unique_conosament, unique_product, unique_package);
 X   ALTER TABLE ONLY public.inner_holder DROP CONSTRAINT unique_conosament_product_package;
       public                 chiga    false    228    228    228                       2606    17023 '   export_holder unique_export_combination 
   CONSTRAINT     �   ALTER TABLE ONLY public.export_holder
    ADD CONSTRAINT unique_export_combination UNIQUE (unique_conosament, unique_product, unique_package);
 Q   ALTER TABLE ONLY public.export_holder DROP CONSTRAINT unique_export_combination;
       public                 chiga    false    236    236    236                       2606    16853    inner_holder unique_package 
   CONSTRAINT     `   ALTER TABLE ONLY public.inner_holder
    ADD CONSTRAINT unique_package UNIQUE (unique_package);
 E   ALTER TABLE ONLY public.inner_holder DROP CONSTRAINT unique_package;
       public                 chiga    false    228                       2606    16851    inner_holder unique_product 
   CONSTRAINT     `   ALTER TABLE ONLY public.inner_holder
    ADD CONSTRAINT unique_product UNIQUE (unique_product);
 E   ALTER TABLE ONLY public.inner_holder DROP CONSTRAINT unique_product;
       public                 chiga    false    228                       2606    17025 )   storage_holder unique_storage_combination 
   CONSTRAINT     �   ALTER TABLE ONLY public.storage_holder
    ADD CONSTRAINT unique_storage_combination UNIQUE (unique_conosament, unique_product, unique_package);
 S   ALTER TABLE ONLY public.storage_holder DROP CONSTRAINT unique_storage_combination;
       public                 chiga    false    230    230    230            �           2606    16618    vessels vessels_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public.vessels
    ADD CONSTRAINT vessels_pkey PRIMARY KEY (name_rus);
 >   ALTER TABLE ONLY public.vessels DROP CONSTRAINT vessels_pkey;
       public                 chiga    false    218            3           2620    16975    conosaments insert_into_export    TRIGGER     �   CREATE TRIGGER insert_into_export AFTER INSERT ON public.conosaments FOR EACH ROW EXECUTE FUNCTION public.add_to_export_holder();
 7   DROP TRIGGER insert_into_export ON public.conosaments;
       public               chiga    false    226    240            4           2620    16884    conosaments insert_into_holder    TRIGGER     �   CREATE TRIGGER insert_into_holder AFTER INSERT ON public.conosaments FOR EACH ROW EXECUTE FUNCTION public.add_to_inner_holder();
 7   DROP TRIGGER insert_into_holder ON public.conosaments;
       public               chiga    false    241    226            5           2620    16901    conosaments insert_into_storage    TRIGGER     �   CREATE TRIGGER insert_into_storage AFTER INSERT ON public.conosaments FOR EACH ROW EXECUTE FUNCTION public.add_to_storage_holder();
 8   DROP TRIGGER insert_into_storage ON public.conosaments;
       public               chiga    false    226    239            "           2606    17013 (   agreement_info agreement_info_buyer_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.agreement_info
    ADD CONSTRAINT agreement_info_buyer_fkey FOREIGN KEY (buyer) REFERENCES public.clients_export(name_short);
 R   ALTER TABLE ONLY public.agreement_info DROP CONSTRAINT agreement_info_buyer_fkey;
       public               chiga    false    222    223    4855            $           2606    16824 +   conosaments conosaments_operation_type_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.conosaments
    ADD CONSTRAINT conosaments_operation_type_fkey FOREIGN KEY (operation_type) REFERENCES public.operations(name_operation);
 U   ALTER TABLE ONLY public.conosaments DROP CONSTRAINT conosaments_operation_type_fkey;
       public               chiga    false    4859    224    226            %           2606    16819 '   conosaments conosaments_production_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.conosaments
    ADD CONSTRAINT conosaments_production_fkey FOREIGN KEY (production) REFERENCES public.productions(product_name);
 Q   ALTER TABLE ONLY public.conosaments DROP CONSTRAINT conosaments_production_fkey;
       public               chiga    false    217    226    4845            &           2606    16814 &   conosaments conosaments_transport_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.conosaments
    ADD CONSTRAINT conosaments_transport_fkey FOREIGN KEY (transport) REFERENCES public.transports(name_rus);
 P   ALTER TABLE ONLY public.conosaments DROP CONSTRAINT conosaments_transport_fkey;
       public               chiga    false    219    4849    226            '           2606    16809 #   conosaments conosaments_vessel_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.conosaments
    ADD CONSTRAINT conosaments_vessel_fkey FOREIGN KEY (vessel) REFERENCES public.vessels(name_rus);
 M   ALTER TABLE ONLY public.conosaments DROP CONSTRAINT conosaments_vessel_fkey;
       public               chiga    false    218    4847    226            0           2606    16987    export export_contract_num_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.export
    ADD CONSTRAINT export_contract_num_fkey FOREIGN KEY (contract_num) REFERENCES public.agreement_info(number_unique);
 I   ALTER TABLE ONLY public.export DROP CONSTRAINT export_contract_num_fkey;
       public               chiga    false    238    4857    223            1           2606    16997    export export_package_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.export
    ADD CONSTRAINT export_package_fkey FOREIGN KEY (package) REFERENCES public.export_holder(unique_package);
 D   ALTER TABLE ONLY public.export DROP CONSTRAINT export_package_fkey;
       public               chiga    false    4891    236    238            2           2606    16992    export export_product_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.export
    ADD CONSTRAINT export_product_fkey FOREIGN KEY (product) REFERENCES public.export_holder(unique_product);
 D   ALTER TABLE ONLY public.export DROP CONSTRAINT export_product_fkey;
       public               chiga    false    238    236    4893            (           2606    17003    conosaments fk_company    FK CONSTRAINT     �   ALTER TABLE ONLY public.conosaments
    ADD CONSTRAINT fk_company FOREIGN KEY (company) REFERENCES public.company_rus(name_short);
 @   ALTER TABLE ONLY public.conosaments DROP CONSTRAINT fk_company;
       public               chiga    false    226    4851    220            #           2606    17008    agreement_info fk_company    FK CONSTRAINT     �   ALTER TABLE ONLY public.agreement_info
    ADD CONSTRAINT fk_company FOREIGN KEY (seller) REFERENCES public.company_rus(name_short);
 C   ALTER TABLE ONLY public.agreement_info DROP CONSTRAINT fk_company;
       public               chiga    false    4851    223    220            )           2606    16928 %   inner_market inner_market_client_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.inner_market
    ADD CONSTRAINT inner_market_client_fkey FOREIGN KEY (client) REFERENCES public.clients_rus(name_short);
 O   ALTER TABLE ONLY public.inner_market DROP CONSTRAINT inner_market_client_fkey;
       public               chiga    false    221    4853    232            *           2606    16913 -   inner_market inner_market_conosament_num_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.inner_market
    ADD CONSTRAINT inner_market_conosament_num_fkey FOREIGN KEY (conosament_num) REFERENCES public.inner_holder(unique_conosament);
 W   ALTER TABLE ONLY public.inner_market DROP CONSTRAINT inner_market_conosament_num_fkey;
       public               chiga    false    4865    232    228            +           2606    16923 &   inner_market inner_market_package_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.inner_market
    ADD CONSTRAINT inner_market_package_fkey FOREIGN KEY (package) REFERENCES public.inner_holder(unique_package);
 P   ALTER TABLE ONLY public.inner_market DROP CONSTRAINT inner_market_package_fkey;
       public               chiga    false    4869    228    232            ,           2606    16918 )   inner_market inner_market_production_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.inner_market
    ADD CONSTRAINT inner_market_production_fkey FOREIGN KEY (production) REFERENCES public.inner_holder(unique_product);
 S   ALTER TABLE ONLY public.inner_market DROP CONSTRAINT inner_market_production_fkey;
       public               chiga    false    232    4871    228            -           2606    16944 !   storage storage_contract_num_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.storage
    ADD CONSTRAINT storage_contract_num_fkey FOREIGN KEY (contract_num) REFERENCES public.agreement_info(number_unique);
 K   ALTER TABLE ONLY public.storage DROP CONSTRAINT storage_contract_num_fkey;
       public               chiga    false    4857    234    223            .           2606    16954    storage storage_package_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.storage
    ADD CONSTRAINT storage_package_fkey FOREIGN KEY (package) REFERENCES public.storage_holder(unique_package);
 F   ALTER TABLE ONLY public.storage DROP CONSTRAINT storage_package_fkey;
       public               chiga    false    234    4877    230            /           2606    16949    storage storage_product_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.storage
    ADD CONSTRAINT storage_product_fkey FOREIGN KEY (product) REFERENCES public.storage_holder(unique_product);
 F   ALTER TABLE ONLY public.storage DROP CONSTRAINT storage_product_fkey;
       public               chiga    false    4879    234    230            �   x   x�314�76�43�700�4204�50�50�0���38�C<��ML@jL���� 5�&�F05��y�E�y\&���U�[ta��Y`�L-L`cS㟜��������� :�+�      �   �   x�u�1k�0Fg�W�j"%�m��!n.�C�.�-�G�S�,J��kA��n����ޮ*�]U�ܝ>���O8���+��9R����9��q�\��$��/l��2�7:ӑA��#T�%���A<�/�����u��@�\ê�A�,/g�W�{)��Q���D��bd:D�!A4�݈�@��ѻ��+`�'�|����ތX,�jq̦O+q���/�m���/�	l;      �   
  x���]j�@���*�y����$�_lZ���I+�/�vJ�Ī����ț��:20s��p�7c��q��0�s���E�"^f]�XUu*y�0�N�7�y��-`<�4�ϪͪauT;�i��Iň�V#ROW'(ټ׳h�Ah�&�9�n�$6|c����m�q�t���t_�fB�֔Ŗ���B0�}a��-?�k�)z�~�3��;�3�)���?��%�{�g�kB����+�x���/eP2c
�zij��eY'���      �   �   x�����8/�A��;.�^l��}a�]�]أ����QT������������Y������d�P������L,,L�t���� � �C#��X�;�$dllifh�TJL)J-.��	�/*Q(.���MLOLI�iI�OI�/.N�00 �\�ua΅�f�\�m��Y(�C��Q785Q�3�$�(/�$3?/1���͉p�!���q>PW� ��x      �   �  x����N�@���O1/`{~�w�(eQĊ�	A�@T,���*�@b�&!��g��P¢��s}�s�#�o�*5i�m�t��Ъ�aLQ{[;C|�m�;�#��Z����7�^��R���b/y�������L�6w�Z㙪�uᤕ���ð�s��^�).��B�!�#@�=)����J}�s|��F���H�z�U���U=@�s�DL��ga�
y�4�p�7�H���x y���0BY���q�G�+�|kFp�׃Ӎ���^�:��!��yI|
�I������D�V$�͞���z�0�#S5�|�Tb���F�BJ�:�mAoWth��K�q��=�I�t:Һp��{3_�=F�o��֔�\	���4��ծ�[�O��M
�J^��N��I4���}�o�WnE�
z�M6z����cH�nw�,˞ �V��      �   �   x�]α�@��7��%��r�]�DHJ�0�T�@�!HP0��N��_v��=9E*(�GyG�R�D9PQG���m�w���9r����#���z�5���t��@
����Z!ڵa���t����8c(Rc��������e槓�Z0���d��b�c��>>�      �   M   x�3�42�7�0�{/6]�pa���6s�p�p���r^���taP�b#HU��� T��Ӑ+F��� Z$�      �   \   x�˱� ��n
&��4�Zؐ���`�6*3���T�z�����N&��2J�5H�l\9�N��q sA6xQQp��U/qN�FU�k-      �   �   x�u�=N�`��9�w ��/_�,�#�	e`��(p�T���d����H5�;�z�������Z��Q�m�m�UTb$�9ح������=D����I6��	�"�bZ<�ʢje*� �;��Ɇ4@ �A��`�M�%nJ{�yo/!�E����?}Tj��w�Q���(��	z�7~iS��~e{�چ+S�L����#0��y������������      �   H   x�����ދ��.6\�za/S�b��n s߅]\{/��xa��}@�&���@��r[�J�r��qqq �?,�      �   '  x�5�=N�@�z�s '!\ ��&�co�*�9KT!)(���
!!q '`�?�+��c#��63ߛ����-����sSq��D�הy��K�b��͐cKXy�k��=�ps쐓��g�P"wKq�T�HO"�Q����~�sU�����'�A�4�ڨ��6��$��?�v�/�#��s�s��a8�rST�����X)3�CS��J|4�E3���6b�z�:�!��1*�L�M�:&?y�XѨ�i�H�0��-1�7���Xͱ��N�E}�zs2�^���jI)���      �   �   x�]�1�@�z�{ Y���"��Z���aԃ
O`BB�h�	�	$6�_����� e�IXBI�Y��@� ���6AEؐ^���>�{[����>�]��3f�4B>�я����?>���ه��r�K���ۄ7���'m��>�%I��cW����c�m$:a      �   K   x�3�4�7�0���;.��}
6�_��ih�e$�uC|8/,�nU��t���֋�v]��id�g����� ���      �   �   x��0��6p�T%rV+%秤*Y)(�)�(�y�%E�y��E% q#�Z��.l��	�q��~ΐĲ�Ld�!a85�4O����. ��错�������Nc��I�/l��h�fΰʤ��t$�aN85�@5_ljn����8��8Yw0N݆@�1z\\\ M�oR      �   b  x����J�@���S,{V��
ޤ�l����ņ�	$*�R�>�xAA�X�b��g�������{���|��<��������P��hH���=���%MʎV�i��ŝ��y<����50�ks�Dܛަ�QLe���x6��2�����������Y��T���-����H�kXB�����d�u�8G�Gl\r���.v����8��#]!C�,�_���H�%���h\r�yk$�Z	W�pU	WJ<���Aη�{����N5ڭD�i۲8o�H�����8�*��S|�WC��!I���,���q�{�"x�۝�v'$ƨ7",�L�Zª��U	[�-��t]�]�&      