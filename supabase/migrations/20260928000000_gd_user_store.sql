-- 广东导游备考台 · 云同步（测试版）
-- 每个用户每类资料一行：cards（卡片记忆标记/划线）、check（考点打卡）、user（修改、笔记、导游词划线）、cd（倒计时）
create table if not exists public.gd_user_store (
  user_id    uuid        not null default auth.uid() references auth.users (id) on delete cascade,
  store      text        not null check (store in ('cards', 'check', 'user', 'cd')),
  data       jsonb       not null,
  updated_at timestamptz not null default now(),
  primary key (user_id, store),
  constraint gd_user_store_size check (octet_length(data::text) < 2000000)
);

alter table public.gd_user_store enable row level security;

-- 只能读写自己的资料
create policy "gd_user_store select own" on public.gd_user_store
  for select to authenticated using ((select auth.uid()) = user_id);
create policy "gd_user_store insert own" on public.gd_user_store
  for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "gd_user_store update own" on public.gd_user_store
  for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "gd_user_store delete own" on public.gd_user_store
  for delete to authenticated using ((select auth.uid()) = user_id);

revoke all on public.gd_user_store from anon;
grant select, insert, update, delete on public.gd_user_store to authenticated;
revoke truncate, references, trigger on public.gd_user_store from authenticated;
