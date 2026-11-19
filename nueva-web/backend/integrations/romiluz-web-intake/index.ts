import postgres from 'npm:postgres@3.4.7';
import {createHandler} from './handler.mjs';
let connection;
const database=()=>{if(!connection)connection=postgres(Deno.env.get('SUPABASE_DB_URL'),{prepare:false,max:1,idle_timeout:20,connect_timeout:10,ssl:{rejectUnauthorized:true}});return connection;};
Deno.serve(createHandler({database,keyHash:'aaf528db034066098f95a469e2d8512a4fa2d7c0e39a6f5d5e9399af4ebff6ff',owner:'76d3dd21-64b4-41e8-b178-cf4bef76bce9'}));
