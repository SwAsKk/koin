-- V3: Triggers and Functions for automatic balance updates and debt management

-- Function to update bank account balance when transaction is created
CREATE OR REPLACE FUNCTION update_bank_account_balance()
RETURNS TRIGGER AS $$
BEGIN
    -- Update bank account balance
    IF NEW.bank_account_id IS NOT NULL THEN
        IF NEW.type_id = 1 THEN -- Income
            UPDATE bank_accounts 
            SET balance = balance + NEW.value 
            WHERE id = NEW.bank_account_id;
        ELSE -- Expense or Transfer
            UPDATE bank_accounts 
            SET balance = balance - NEW.value 
            WHERE id = NEW.bank_account_id;
        END IF;
    END IF;
    
    -- Update investment account balance if applicable
    IF NEW.investment_account_id IS NOT NULL THEN
        IF NEW.type_id = 1 THEN -- Income
            UPDATE investment_accounts 
            SET balance = balance + NEW.value 
            WHERE id = NEW.investment_account_id;
        ELSE -- Expense or Transfer
            UPDATE investment_accounts 
            SET balance = balance - NEW.value 
            WHERE id = NEW.investment_account_id;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to update bank account balance when transaction is updated
CREATE OR REPLACE FUNCTION update_bank_account_balance_on_update()
RETURNS TRIGGER AS $$
BEGIN
    -- Revert old transaction impact
    IF OLD.bank_account_id IS NOT NULL THEN
        IF OLD.type_id = 1 THEN -- Income
            UPDATE bank_accounts 
            SET balance = balance - OLD.value 
            WHERE id = OLD.bank_account_id;
        ELSE -- Expense or Transfer
            UPDATE bank_accounts 
            SET balance = balance + OLD.value 
            WHERE id = OLD.bank_account_id;
        END IF;
    END IF;
    
    IF OLD.investment_account_id IS NOT NULL THEN
        IF OLD.type_id = 1 THEN -- Income
            UPDATE investment_accounts 
            SET balance = balance - OLD.value 
            WHERE id = OLD.investment_account_id;
        ELSE -- Expense or Transfer
            UPDATE investment_accounts 
            SET balance = balance + OLD.value 
            WHERE id = OLD.investment_account_id;
        END IF;
    END IF;
    
    -- Apply new transaction impact
    IF NEW.bank_account_id IS NOT NULL THEN
        IF NEW.type_id = 1 THEN -- Income
            UPDATE bank_accounts 
            SET balance = balance + NEW.value 
            WHERE id = NEW.bank_account_id;
        ELSE -- Expense or Transfer
            UPDATE bank_accounts 
            SET balance = balance - NEW.value 
            WHERE id = NEW.bank_account_id;
        END IF;
    END IF;
    
    IF NEW.investment_account_id IS NOT NULL THEN
        IF NEW.type_id = 1 THEN -- Income
            UPDATE investment_accounts 
            SET balance = balance + NEW.value 
            WHERE id = NEW.investment_account_id;
        ELSE -- Expense or Transfer
            UPDATE investment_accounts 
            SET balance = balance - NEW.value 
            WHERE id = NEW.investment_account_id;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to update bank account balance when transaction is deleted
CREATE OR REPLACE FUNCTION update_bank_account_balance_on_delete()
RETURNS TRIGGER AS $$
BEGIN
    -- Revert transaction impact
    IF OLD.bank_account_id IS NOT NULL THEN
        IF OLD.type_id = 1 THEN -- Income
            UPDATE bank_accounts 
            SET balance = balance - OLD.value 
            WHERE id = OLD.bank_account_id;
        ELSE -- Expense or Transfer
            UPDATE bank_accounts 
            SET balance = balance + OLD.value 
            WHERE id = OLD.bank_account_id;
        END IF;
    END IF;
    
    IF OLD.investment_account_id IS NOT NULL THEN
        IF OLD.type_id = 1 THEN -- Income
            UPDATE investment_accounts 
            SET balance = balance - OLD.value 
            WHERE id = OLD.investment_account_id;
        ELSE -- Expense or Transfer
            UPDATE investment_accounts 
            SET balance = balance + OLD.value 
            WHERE id = OLD.investment_account_id;
        END IF;
    END IF;
    
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Function to create debt records when shared expense is created
CREATE OR REPLACE FUNCTION create_debts_for_shared_expense()
RETURNS TRIGGER AS $$
DECLARE
    expense_amount DECIMAL(15,2);
    expense_type TEXT;
    expense_id INTEGER;
    group_members_count INTEGER;
    share_amount DECIMAL(15,2);
    member_record RECORD;
BEGIN
    -- Only process if this is a shared expense
    IF NEW.is_shared = TRUE AND NEW.group_id IS NOT NULL THEN
        expense_amount := NEW.value;
        expense_type := 'transaction';
        expense_id := NEW.id;
        
        -- Get count of group members (excluding the payer)
        SELECT COUNT(*) INTO group_members_count
        FROM group_members 
        WHERE group_id = NEW.group_id AND user_id != NEW.user_id;
        
        -- Calculate share amount per person
        IF group_members_count > 0 THEN
            share_amount := expense_amount / (group_members_count + 1);
            
            -- Create debt records for each group member
            FOR member_record IN 
                SELECT user_id 
                FROM group_members 
                WHERE group_id = NEW.group_id AND user_id != NEW.user_id
            LOOP
                -- Insert into expense_shares
                INSERT INTO expense_shares (
                    expense_id, 
                    expense_type, 
                    user_id, 
                    share_amount, 
                    share_percentage
                ) VALUES (
                    expense_id, 
                    expense_type, 
                    member_record.user_id, 
                    share_amount, 
                    (share_amount / expense_amount) * 100
                );
                
                -- Insert into debts
                INSERT INTO debts (
                    creditor_id, 
                    debtor_id, 
                    amount, 
                    description, 
                    expense_id, 
                    expense_type
                ) VALUES (
                    NEW.user_id, 
                    member_record.user_id, 
                    share_amount, 
                    'Долг по общей трате: ' || NEW.name
                );
            END LOOP;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to create debt records when trip expense is created
CREATE OR REPLACE FUNCTION create_debts_for_trip_expense()
RETURNS TRIGGER AS $$
DECLARE
    trip_participants_count INTEGER;
    share_amount DECIMAL(15,2);
    participant_record RECORD;
BEGIN
    -- Get count of trip participants (excluding the payer)
    SELECT COUNT(*) INTO trip_participants_count
    FROM trip_participants 
    WHERE trip_id = NEW.trip_id AND user_id != NEW.paid_by;
    
    -- Calculate share amount per person
    IF trip_participants_count > 0 THEN
        share_amount := NEW.amount / (trip_participants_count + 1);
        
        -- Create debt records for each participant
        FOR participant_record IN 
            SELECT user_id 
            FROM trip_participants 
            WHERE trip_id = NEW.trip_id AND user_id != NEW.paid_by
        LOOP
            -- Insert into expense_shares
            INSERT INTO expense_shares (
                expense_id, 
                expense_type, 
                user_id, 
                share_amount, 
                share_percentage
            ) VALUES (
                NEW.id, 
                'trip_expense', 
                participant_record.user_id, 
                share_amount, 
                (share_amount / NEW.amount) * 100
            );
            
            -- Insert into debts
            INSERT INTO debts (
                creditor_id, 
                debtor_id, 
                amount, 
                description, 
                expense_id, 
                expense_type
            ) VALUES (
                NEW.paid_by, 
                participant_record.user_id, 
                share_amount, 
                'Долг по поездке: ' || NEW.name
            );
        END LOOP;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers
CREATE TRIGGER trigger_update_bank_balance_on_insert
    AFTER INSERT ON trans
    FOR EACH ROW
    EXECUTE FUNCTION update_bank_account_balance();

CREATE TRIGGER trigger_update_bank_balance_on_update
    AFTER UPDATE ON trans
    FOR EACH ROW
    EXECUTE FUNCTION update_bank_account_balance_on_update();

CREATE TRIGGER trigger_update_bank_balance_on_delete
    AFTER DELETE ON trans
    FOR EACH ROW
    EXECUTE FUNCTION update_bank_account_balance_on_delete();

CREATE TRIGGER trigger_create_debts_for_shared_expense
    AFTER INSERT ON trans
    FOR EACH ROW
    EXECUTE FUNCTION create_debts_for_shared_expense();

CREATE TRIGGER trigger_create_debts_for_trip_expense
    AFTER INSERT ON trip_expenses
    FOR EACH ROW
    EXECUTE FUNCTION create_debts_for_trip_expense();

CREATE TRIGGER trigger_update_trans_updated_at
    BEFORE UPDATE ON trans
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_debts_updated_at
    BEFORE UPDATE ON debts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to get user's total balance across all accounts
CREATE OR REPLACE FUNCTION get_user_total_balance(user_id_param INTEGER)
RETURNS TABLE(
    total_bank_balance DECIMAL(15,2),
    total_investment_balance DECIMAL(15,2),
    total_balance DECIMAL(15,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COALESCE(SUM(ba.balance), 0) as total_bank_balance,
        COALESCE(SUM(ia.balance), 0) as total_investment_balance,
        COALESCE(SUM(ba.balance), 0) + COALESCE(SUM(ia.balance), 0) as total_balance
    FROM users u
    LEFT JOIN bank_accounts ba ON u.id = ba.user_id AND ba.is_active = TRUE
    LEFT JOIN investment_accounts ia ON u.id = ia.user_id AND ia.is_active = TRUE
    WHERE u.id = user_id_param;
END;
$$ LANGUAGE plpgsql;

-- Function to get user's debts summary
CREATE OR REPLACE FUNCTION get_user_debts_summary(user_id_param INTEGER)
RETURNS TABLE(
    owes_total DECIMAL(15,2),
    owed_total DECIMAL(15,2),
    net_balance DECIMAL(15,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COALESCE(SUM(CASE WHEN debtor_id = user_id_param THEN amount ELSE 0 END), 0) as owes_total,
        COALESCE(SUM(CASE WHEN creditor_id = user_id_param THEN amount ELSE 0 END), 0) as owed_total,
        COALESCE(SUM(CASE WHEN creditor_id = user_id_param THEN amount ELSE 0 END), 0) - 
        COALESCE(SUM(CASE WHEN debtor_id = user_id_param THEN amount ELSE 0 END), 0) as net_balance
    FROM debts
    WHERE (debtor_id = user_id_param OR creditor_id = user_id_param) 
    AND is_settled = FALSE;
END;
$$ LANGUAGE plpgsql; 