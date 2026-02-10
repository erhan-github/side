import { NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';

export async function GET(request: Request) {
    try {
        const supabase = await createClient();
        const { data: { user } } = await supabase.auth.getUser();

        if (!user) {
            return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
        }

        const { searchParams } = new URL(request.url);
        const action = searchParams.get('action') || 'alerts';
        const projectId = searchParams.get('project_id');

        let data;
        let error;
        let count;

        switch (action) {
            case 'alerts': {
                const limit = parseInt(searchParams.get('limit') || '50');
                const offset = parseInt(searchParams.get('offset') || '0');

                let alertsQuery = supabase
                    .from('findings')
                    .select('*', { count: 'exact' })
                    .eq('user_id', user.id)
                    .eq('is_resolved', false);

                if (projectId) {
                    alertsQuery = alertsQuery.eq('project_id', projectId);
                }

                const { data: alertsData, error: alertsError, count: alertsCount } = await alertsQuery
                    .order('created_at', { ascending: false })
                    .range(offset, offset + limit - 1);

                if (alertsError) throw alertsError;
                return NextResponse.json({ data: alertsData, count: alertsCount });
            }

            case 'activities':
                let activitiesQuery = supabase
                    .from('activities')
                    .select('*')
                    .eq('user_id', user.id)
                    .order('created_at', { ascending: false })
                    .limit(50);

                if (projectId) {
                    activitiesQuery = activitiesQuery.eq('project_id', projectId);
                }

                ({ data, error } = await activitiesQuery);
                if (error) throw error;
                return NextResponse.json(data);

            case 'profile':
                ({ data, error } = await supabase
                    .from('profiles')
                    .select('*')
                    .eq('id', user.id)
                    .single());

                if (error) throw error;
                return NextResponse.json({
                    tier: data?.tier || 'free',
                    balance: (data?.tokens_monthly || 0) - (data?.tokens_used || 0)
                });

            case 'iq': {
                // Simple IQ calculation: 100 - (active findings * weight)
                const { count: iqCount, error: countError } = await supabase
                    .from('findings')
                    .select('*', { count: 'exact', head: true })
                    .eq('user_id', user.id)
                    .eq('is_resolved', false);

                if (countError) throw countError;

                const score = Math.max(0, 100 - (iqCount || 0) * 5);
                return NextResponse.json({ score, findings_count: iqCount });
            }

            default:
                return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
        }
    } catch (error: any) {
        console.error('API Error:', error);
        return NextResponse.json(
            { error: error.message || 'Internal server error' },
            { status: 500 }
        );
    }
}

export async function POST(request: Request) {
    try {
        const supabase = await createClient();
        const { data: { user } } = await supabase.auth.getUser();

        if (!user) {
            return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
        }

        const body = await request.json();
        const { action, finding_id } = body;

        if (action === 'resolve' && finding_id) {
            const { error } = await supabase
                .from('findings')
                .update({ is_resolved: true, resolved_at: new Date().toISOString() })
                .eq('id', finding_id)
                .eq('user_id', user.id);

            if (error) throw error;
            return NextResponse.json({ success: true });
        }

        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    } catch (error: any) {
        console.error('API Error:', error);
        return NextResponse.json(
            { error: error.message || 'Internal server error' },
            { status: 500 }
        );
    }
}
