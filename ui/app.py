import streamlit as st
import psycopg2
import redis
import os
import json
import sys
import time
from datetime import datetime, timedelta
import pandas as pd

# Add parent directory to path
sys.path.append('/app')
from master.main import run_master, init_database

# Initialize connections
@st.cache_resource
def get_connections():
    redis_client = redis.from_url(os.getenv("REDIS_URL"))
    pg_conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    return redis_client, pg_conn

# Page config
st.set_page_config(
    page_title="Infinite Crew Control Center",
    page_icon="🤖",
    layout="wide"
)

st.title("🚀 Infinite Crew Control Center")
st.markdown("*Autonomous agents that spawn autonomous agents*")

# Get connections
redis_client, pg_conn = get_connections()

# Initialize database
init_database()

# Sidebar for stats
with st.sidebar:
    st.header("📊 System Status")
    
    # Auto-refresh
    auto_refresh = st.checkbox("Auto-refresh (5s)", value=False)
    if auto_refresh:
        time.sleep(5)
        st.rerun()
    
    # Queue size
    queue_size = redis_client.llen("tasks")
    st.metric("Tasks in Queue", queue_size)
    
    # Database stats
    with pg_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM results")
        total_results = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM results WHERE created_at > NOW() - INTERVAL '1 hour'")
        recent_results = cur.fetchone()[0]
    
    st.metric("Total Results", total_results)
    st.metric("Results (Last Hour)", recent_results)
    
    # Clear options
    st.divider()
    if st.button("🗑️ Clear Queue", type="secondary"):
        redis_client.delete("tasks")
        st.success("Queue cleared!")
        st.rerun()

# Main content area
tab1, tab2, tab3, tab4 = st.tabs(["🎯 New Mission", "📋 Active Tasks", "📊 Results", "🌳 Task Tree"])

with tab1:
    st.header("Launch New Mission")
    
    # Mission input
    mission = st.text_area(
        "Enter your mission:",
        placeholder="Example: Write a comprehensive guide about quantum computing, then create a Python tutorial implementing the concepts, and finally design a quiz to test understanding.",
        height=150
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🚀 Launch Mission", type="primary", disabled=not mission):
            with st.spinner("Decomposing mission..."):
                run_master(mission)
            st.success("Mission launched! Check the Active Tasks tab.")
            time.sleep(2)
            st.rerun()
    
    # Example missions
    st.subheader("Example Missions")
    examples = [
        "Research the latest developments in AI safety and write a 1000-word article",
        "Create a business plan for a sustainable coffee shop, including market analysis and financial projections",
        "Design a mobile app for habit tracking, create mockups, and write the technical specification",
        "Analyze Shakespeare's Hamlet, write a modern adaptation, and create a study guide"
    ]
    
    for example in examples:
        if st.button(f"📝 {example[:60]}...", key=example):
            run_master(example)
            st.success("Example mission launched!")
            st.rerun()

with tab2:
    st.header("Active Tasks in Queue")
    
    if queue_size == 0:
        st.info("No active tasks in queue. Launch a mission to get started!")
    else:
        # Get all tasks from queue
        tasks = []
        for i in range(min(queue_size, 50)):  # Limit to 50 for performance
            task_json = redis_client.lindex("tasks", i)
            if task_json:
                task = json.loads(task_json)
                tasks.append(task)
        
        # Display as dataframe
        if tasks:
            df = pd.DataFrame(tasks)
            df['prompt_preview'] = df['prompt'].str[:100] + '...'
            df = df[['task_id', 'depth', 'prompt_preview', 'parent_id']]
            
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "task_id": st.column_config.TextColumn("Task ID", width="small"),
                    "depth": st.column_config.NumberColumn("Depth", width="small"),
                    "prompt_preview": st.column_config.TextColumn("Task", width="large"),
                    "parent_id": st.column_config.TextColumn("Parent", width="small")
                }
            )

with tab3:
    st.header("Completed Results")
    
    # Time filter
    time_filter = st.selectbox(
        "Time Range:",
        ["All Time", "Last Hour", "Last 24 Hours", "Last Week"]
    )
    
    # Build query
    query = "SELECT id, prompt, output, depth, created_at FROM results"
    if time_filter == "Last Hour":
        query += " WHERE created_at > NOW() - INTERVAL '1 hour'"
    elif time_filter == "Last 24 Hours":
        query += " WHERE created_at > NOW() - INTERVAL '24 hours'"
    elif time_filter == "Last Week":
        query += " WHERE created_at > NOW() - INTERVAL '7 days'"
    query += " ORDER BY created_at DESC LIMIT 20"
    
    # Get results
    with pg_conn.cursor() as cur:
        cur.execute(query)
        results = cur.fetchall()
    
    if not results:
        st.info("No results found for the selected time range.")
    else:
        for result in results:
            task_id, prompt, output, depth, created_at = result
            
            with st.expander(f"🎯 {prompt[:80]}...", expanded=False):
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    st.caption(f"Depth: {depth}")
                with col2:
                    st.caption(f"ID: {str(task_id)[:8]}...")
                with col3:
                    st.caption(f"Completed: {created_at.strftime('%Y-%m-%d %H:%M')}")
                
                st.divider()
                st.markdown("**Task:**")
                st.text(prompt)
                st.markdown("**Output:**")
                st.text(output[:2000] + ("..." if len(output) > 2000 else ""))

with tab4:
    st.header("Task Hierarchy Tree")
    
    # Get task hierarchy
    with pg_conn.cursor() as cur:
        cur.execute("""
            WITH RECURSIVE task_tree AS (
                SELECT id, parent_id, prompt, depth, output IS NOT NULL as completed
                FROM results
                WHERE parent_id IS NULL
                
                UNION ALL
                
                SELECT r.id, r.parent_id, r.prompt, r.depth, r.output IS NOT NULL
                FROM results r
                JOIN task_tree t ON r.parent_id = t.id
            )
            SELECT * FROM task_tree
            ORDER BY depth, id
            LIMIT 100
        """)
        tree_data = cur.fetchall()
    
    if not tree_data:
        st.info("No task hierarchies found. Complete some multi-level missions to see the tree!")
    else:
        # Build tree visualization
        st.markdown("### Task Dependencies")
        
        # Group by parent
        tree_dict = {}
        for task_id, parent_id, prompt, depth, completed in tree_data:
            if parent_id is None:
                if task_id not in tree_dict:
                    tree_dict[task_id] = {
                        'prompt': prompt,
                        'depth': depth,
                        'completed': completed,
                        'children': []
                    }
            else:
                if parent_id not in tree_dict:
                    tree_dict[parent_id] = {'children': []}
                tree_dict[parent_id]['children'].append({
                    'id': task_id,
                    'prompt': prompt,
                    'depth': depth,
                    'completed': completed
                })
        
        # Display tree
        for root_id, root_data in tree_dict.items():
            if 'prompt' in root_data:
                status = "✅" if root_data['completed'] else "⏳"
                st.markdown(f"**{status} Root:** {root_data['prompt'][:100]}...")
                
                for child in root_data.get('children', []):
                    status = "✅" if child['completed'] else "⏳"
                    st.markdown(f"  └─ {status} {child['prompt'][:80]}...")

# Footer
st.divider()
st.caption("Infinite Crew - Autonomous agents orchestrating autonomous agents 🤖")
